# Pmacs: the editor reconstructed from the held manuals and call sites

Status 2026-11-27. SIMPOS's Pmacs editor is lost: no source, no binary,
and the SIMPOS User's and Operating Manuals, which would describe it, are
**not held**. This file gathers what the held manuals and the held
programs say about Pmacs, and specifies the stand-ins built from it
(`psi/standin/standard_editor.esp`, `pmacs_window.esp`,
`pmacs_display.esp`, `editor_text_buffer.esp`,
`editor_command_interpreter.esp`; `pmacs_standard_editor.esp` inherits
all of it). It extends window.md §2.11 and §5.2, which list the classes,
the screen form and the binding forms.

## 0. Labels

Every behaviour below carries one of three labels (the owner's rule of
2026-11-27, `pim/tools/agent_rules.md`):

- **RECONSTRUCTED-FROM-MANUAL**: a held manual states it. The file and
  page or line are cited.
- **INFERENCE**: not stated anywhere held. It is inferred from held call
  sites, or from Emacs: the ESP manual says Pmacs is "based on Emacs"
  (§1), and that licenses Emacs semantics only as inference, written
  "INFERENCE (Emacs analogy)".
- **OURS**: a modelling choice with no source (names of helper
  selectors, echo-line words, the data layout).

The selectors are graded too. **HELD** means held ICOT code sends the
selector (the call site is cited). **OURS** means the selector exists only
for a binding or a helper. In the stand-in files each method's comment
block carries `INTERPOLATED (selector HELD|OURS, body ...)`
(test_methods_labelled), and it cites the section of this file.
`test_pmacs_methods_labelled` checks two things for every stand-in method
that cites this file: that one of the three labels is present, and that
the selector is named in the table in §5.

## 1. Sources, by weight

| source | where | what it gives |
|---|---|---|
| ESP manual, overview | ESPtex `overview-e.tex:1347-1358`, PDF p25 | Pmacs is "an editor based on Emacs". Pmacs windows are the text I/O windows. "The system manages the text buffer of each Pmacs window consistently": strings are operated on by programs, and "text data can be exchanged between windows or programs in the same way as Pmacs" |
| PIMOS manual (English) | `man15`, PDF p72, p75 | a window is created with a buffer name. `select_buffer` selects a window's text buffer by name and creates it when it is missing |
| | PDF p73 | opening an existing file in write mode makes "the file with the same name ... in higher version" |
| | PDF p76 | `clear` and `get_buffer_name`. A deactivated window keeps its image |
| | PDF p91 | a window's title is "not the text buffer name of the PMACS" |
| | PDF p164 | `:create(#pmacs_window,[size,position,title],W)`, putl, flash |
| PIMOS manual (Japanese) | `man30.j.ps` | three hits, parallel to man15's |
| KWIC manual (IFS application `kwic-esp`, doc/) | `kwod.tex:184`, `:211-260` (index p38) | scrolling "by the pmacs commands", "conforming to SIMPOS-pmacs's cursor movement commands": **ctrl-N / ctrl-P one line, ctrl-V one page forward, meta-V one page back** |
| | `kwike.tex:37` | "it is a pmacs window, its basic operation conforms to pmacs" |
| | `kwme.tex:245-249`, `:372-376`; `kwikm.tex:36` | ctrl-X ctrl-Z ends the editor |
| | `kwiks.tex:62-64` | a pmacs window with a history. ctrl-C ctrl-H or a right click opens the help menu |
| | `kwman.tex:15-40` | the ctrl-/meta- key notation. meta-O cycles child windows |
| KWIC class manual (`kwic-esp-002` doc) | `classSpec.IO2:2805-2960` | the class pmcSTDeditor (nature standard_editor). `command(Inst,A,B)` "assigns a command to a key; called from the editor object", where A is a key or mouse code and B an atom. `control_c` is "the same as command/3". It cites a lost section, "エディタ説明書/PMACSのカスタマイズ/プログラムによる拡張・変更機能" (Editor manual / PMACS customization / extension by program) |
| | `classSpec.doc:1317-1318` | markers drawn "like pmacs's input start point" and "like pmacs's mark": **Pmacs has a mark, and shows it** |
| IPSJ 114007 | `docs/nonlocal/lit/ipsj/114007_KJ00001330813.pdf`, notes `notes/ipsj.md:226-236` | over 100 commands (by character, word, line and page; comments, case, paren matching, narrowing, auto-save). A buffer pool reached by name. A gap buffer. Program macros by subclassing the editor object. Keyboard macros. State variables |
| primer | `primer25.tex:86` | "Edit ... using the PMACS editor" |
| chal INSTALL | `chal/INSTALL:5-11` | "Invoke pmacs", `M-x set_package`, `M-x catalogue_and_save` |
| screenshots | window.md §2.11 | the mode line, the echo line (`Find File:`, `Read! <path>`), the EDITOR MENU |

**Where they are held** (under `docs/nonlocal/`, the files on disk and their rows and
checksums in `IFS_MANIFEST.md` and `LIT_MANIFEST.md`; nothing new is committed):
- ESP manual: `ifs/manuals/esp/ESPtex.tar.Z` (overview-e.tex);
- PIMOS manuals: `ifs/manuals/pimos/man15.ps.Z`, `man30.j.ps.Z` and `primer25.tex.Z`;
- KWIC: `ifs/natural-lang/simpos/kwic-esp.tar.Z` (doc/kw*.tex) and `kwic-esp-002.tar.Z`
  (doc/classSpec.*);
- the programs: papyrus `ifs/solver-prover/simpos/papyrus.tar.Z` (source.tar, demo/EDITOR/);
  cil `ifs/natural-lang/simpos/cil.tar.gz`; kappa2 `ifs/kbms-clp/simpos/kappa2.tar.Z`; cal
  `ifs/kbms-clp/simpos/cal-esp.tar.Z`; chal `ifs/kbms-clp/simpos/chal.tar.Z`; disc
  `ifs/natural-lang/simpos/disc.tar.Z`;
- IPSJ 114007: `lit/ipsj/114007_KJ00001330813.pdf`.

The tests read the three papyrus members in memory (`psi/held.py` MEMBERS
my_syntax, my_delete, my_point).

The manuals carrying most of the weight are the KWIC manual (kwod.tex,
index p38: the page and line commands; classSpec.IO2: the binding
protocol; classSpec.doc: the mark), the ESP manual overview (PDF p25: Emacs
basis, shared text), and PIMOS man15 (PDF p72, p75, p91: named buffers).

## 2. The held call sites the stand-ins serve

| program (IFS source) | site | sends |
|---|---|---|
| papyrus `demo/EDITOR/my_syntax.esp.1` | :22-41 | goto_beginning/1, mark/1; then N times exchange_point/1, backward_character/1 twice (the second inside a failure-catching try), next_term/1; then exception/2 `illegal syntax` |
| papyrus `my_delete.esp.1` | :48 | push_to_yank(Editor,String,forward) after see_position/4. `:control_c(Editor,#"d",delete_proof)` |
| papyrus `my_point.esp.1` | :14-73 | `:command(Editor,mouse#l,goal_with_mouse)`: cursor_with_mouse/1, current_buffer/2, current_position/2. show_menu/1 |
| papyrus `my_changer.esp.1` | :110 | mark/1 after move_to/2 |
| papyrus `my_load.esp.1` | :243, :262 | select_buffer/2, exception/2, find_file/2 |
| papyrus `rule_editor.esp.1` | :30 | an empty two_windows/1 override |
| papyrus `my_search` | | insert(Editor,#"S") |
| cil `src/ds_edt.esp` | :760 | write_file(Editor,Buffer,Name,Pathname), then set_file_name(Buffer,Pathname) |
| | :767 | read_with_prompt(Window,[Prompt,"(",Default,"):"],Answer). An Answer of "" means the default |
| | :915 | find_file(Editor,Item) |
| | :1035-1049 | get_activate_window_count(Window,N). N == 1 gives two_windows(Editor), otherwise exchange_window(Window) |
| kappa2 `user_if/pb/inwin.esp` | :298 | mark/1, putf, goto_beginning/1, getl, set_input_position/1 |
| kappa2 `user_if/pb/typewin.esp` | :303-327 | clear_input/1, clear_buffer, move_to_first, reset_modify_flag (pb_type_editor_dummy, nature standard_editor) |
| kappa2 `utility/rep/REPINDEX.ESP` | :392, :443, :495; REPDB :107, :132; REPRECORD :103 | clear_input/1 |
| cal2.12 / chal `cal_pmacs.esp` | run/4 | set_input_buffer, get_interpreter, get_editor, goto_beginning, set_input_position, activate, command_interpret, deactivate, current_buffer. All were stood in at window M10 (test_win_m10_cal), so cal_pmacs exercises none of the methods added here |

## 3. Bindings

### 3.1 The protocol

RECONSTRUCTED-FROM-MANUAL (KWIC classSpec.IO2:2840-2870). An editor's
bindings are its instance clauses `:command(Editor, Input, Method)`.
Input is a key code or a mouse code (`mouse#l`), or an atom (a menu
item's value). Method is an atom, sent to the editor. `:control_c/3` is
the same, after C-c. The control_x table after C-x has the same form
(HELD, cal-esp dedit.esp:120). A subclass's clauses come before the
inherited ones (TM-388 §3.4), so a held program's binding wins
(test_win_m10_cal, test_win_pmacs_delete).

### 3.2 The default table (gap G6)

The default table is not held. The table in the stand-in is:

| keys | method | label |
|---|---|---|
| C-f C-b C-n C-p C-a C-e C-d C-k DEL, arrows, C-x C-s, C-x C-z, C-x C-b, C-x b, mouse#r | (window M10) | OURS, window.md §5.2. C-n, C-p and C-x C-z also RECONSTRUCTED-FROM-MANUAL (KWIC kwod.tex, kwme.tex) |
| C-v | view_next_screen | RECONSTRUCTED-FROM-MANUAL (KWIC kwod.tex:229-238) |
| ESC v | view_previous_screen | RECONSTRUCTED-FROM-MANUAL that meta-V pages back. ESC as meta is OURS (§3.3) |
| C-@ | mark | INFERENCE (Emacs analogy) |
| C-w, ESC w, C-y | kill_region, copy_region, yank | INFERENCE (Emacs analogy) |
| C-x C-x | exchange_point | INFERENCE (Emacs analogy) |
| C-x C-f, C-x C-w | find_file/1, write_file/1 | INFERENCE (Emacs analogy). The prompt `Find File:` is a SCREENSHOT (esp.wmv) |
| C-x 2, C-x 1, C-x o | two_windows, one_window, other_window | INFERENCE (Emacs analogy) |
| mouse#l | cursor_with_mouse | OURS. The first click on a window selects it. A click on the window already selected feeds it mouse#l, then selects it again as before (coordinator.esp). Every editor inherits this binding, pimfep's pimos_window_editor among them, so a second click in the PIMOS console moves its point too. That is intended, as in Emacs; tour.script and tour_pmacs.script replay to the same frames as before |

### 3.3 Meta

The KWIC manual writes meta- keys (kwman.tex:15-40: meta-V, meta-O). The
PSI keyboard's meta key, if it has one, is not held. The stand-in reads
ESC as a prefix into the table `:escape/3`, as Emacs does (OURS).

## 4. Semantics

### 4.1 Buffers and windows

Covered at window M10: named buffers in a pool, select_buffer/2 (makes
the buffer when it is missing; man15 p72, p75), the mode line and the echo
line (window.md §2.11).

### 4.2 The mark

RECONSTRUCTED-FROM-MANUAL that Pmacs has a mark (KWIC classSpec.doc:1318).
INFERENCE (Emacs analogy) for everything else:
- mark/1 sets the mark at the point and echoes `Mark set` (Emacs's
  words).
- exchange_point/1 swaps the point and the mark. It fails when no mark
  is set.
- The mark is a buffer position, kept inside the text (`editor_text_buffer` set_mark/1, set_mark_at/2,
  get_mark/2, all OURS selectors).

**Gap:** the manual says Pmacs draws its mark on the screen. The stand-in
does not draw it.

### 4.3 The yank buffer

INFERENCE that killed text is one store, shared by every editor. The ESP
overview (PDF p25) says text "can be exchanged between windows or
programs in the same way as Pmacs", through the text buffers the system
manages. It does not mention a kill store, so sharing one is inferred
from that sentence and from Emacs's single kill ring. The stand-in keeps
the store in a class slot of standard_editor, newest first (OURS). No
test yanks in one window what another killed.
- push_to_yank/3 (HELD, my_delete :48) makes String the newest entry.
  Direction is `forward` or `backward` (INFERENCE: Emacs's kill-append
  direction). In the stand-in it changes nothing, and any other direction
  fails.
- kill_line/1 (C-k), kill_region/1 (C-w) and copy_region/1 (ESC w) push
  through push_to_yank/3 with direction forward.
- yank/1 (C-y) inserts the newest entry at the point, leaves the mark
  before it and the point after it, and fails when nothing has been
  killed. INFERENCE.

**Gaps:**
- Consecutive kills do not append, as Emacs's do.
- There is no yank-pop.
- The held named yank buffers (`editor_yank_buffer`, cil ds_bep.esp:2312)
  are a separate store and are not stood in.

### 4.4 next_term

HELD selector (my_syntax :36). Its meaning is INFERENCE, from that one
call site. The loop there is "N times: exchange_point, two
backward_character, next_term", followed by exception/2 at the result.
The only model found under which each pass advances one term is Emacs's
mark-defun applied to ESP terms:
- next_term/1 finds the first term-ending period strictly after the
  point.
- It moves the point to that term's start (past the layout and the
  comments before it), and sets the mark at its end (just after the
  period).
- It fails when no term follows.

A term-ending period is a `.` outside comments (`%` to the end of the
line) and outside quotes, followed by layout or the end of the text
(editor_text_buffer term_region/3, OURS). The model is checked on
`a :- b.` / `c :- d.` / `e.` (§6): for N = 1, 2, 3 the point is left at
the start of term N.

**Gaps:**
- A period inside `/* */` comments, and `0'.` character codes, are not
  recognised.
- The real next_term may move by parse rather than by text.

### 4.5 Prompts

read_with_prompt/3 (HELD selector on the window, cil ds_edt :767). The
parts of the prompt are concatenated and shown in the echo line with the
text typed so far.
- RETURN ends the answer.
- C-g echoes `Quit` and fails.
- BS and DEL rub out a character.

INFERENCE (Emacs's minibuffer); the words are OURS. The caller handles an
empty answer as its default (ds_edt :767).

### 4.6 Paging and the mouse

RECONSTRUCTED-FROM-MANUAL (KWIC kwod.tex:211-238): C-v moves one page
forward and meta-V one page back. The page is the view's text rows
("the range shown"), and the point moves to the new page.
- view_next_screen/1 fails at the end of the text.
- view_previous_screen/1 fails at the top. It leaves the point on the last
  line of the page.

The page's exact size (Emacs keeps two lines of overlap) and where the
point goes are INFERENCE.

cursor_with_mouse/1 (HELD, my_point :23) moves the point to the line and
column under the last click in the active view. A column past the line's
end gives the line's end; a row past the text gives the last line.
INFERENCE.

### 4.7 Two windows

two_windows/1 (HELD, ds_edt :1037; rule_editor overrides it empty) shows
two views of the window, each with its own mode line. INFERENCE (Emacs
analogy, C-x 2).
- The text rows are split (T-1)/2 above the upper view's mode line, and
  the rest below it (OURS).
- get_activate_window_count/2 (HELD) answers 1 or 2.
- exchange_window/1 (HELD, ds_edt :1049) and other_window/1 (HELD, window.md
  §2.11) make the other view active. The other view's buffer becomes the
  interpreter's buffer.
- one_window/1 (C-x 1) goes back to one view.

### 4.8 Files

find_file/2 (HELD, ds_edt :915, my_load :243):
- If a pooled buffer already visits the file, that buffer is selected.
- Otherwise a new buffer is made, named after the identifier of the
  pathname (`demo` for demo.esp: SCREENSHOT IPSJ 36239 p5). The file is
  read into it, and the echo line shows `Read! <full pathname>`, as
  read_file/4 does.
- If the pathname names no file, the result is an empty buffer that a save
  writes there (`New File`, OURS words).

RECONSTRUCTED-FROM-MANUAL that a buffer has a name of its own (man15 p72,
p75, p91). The rest is INFERENCE (Emacs analogy).

write_file/4 (HELD, ds_edt :760) writes the buffer as a new version of
the named file: its latest version + 1, or version 1 of a new file in the
pathname's directory. Afterwards the buffer belongs to that file and is
unmodified, the full pathname is answered, and the echo line shows
`Written! <full pathname>`. Versions are RECONSTRUCTED-FROM-MANUAL only
by analogy (man15 p73; TR-524 p9). The rest is INFERENCE.

find_file/1 (C-x C-f) and write_file/1 (C-x C-w) read the pathname with
read_with_prompt/3.

### 4.9 clear_input

clear_input/1 (HELD, kappa2: before clear_buffer, and before a dump is
written into the buffer) drops whatever was typed and not yet read (the
window's interpreter clear_input/1). INFERENCE: those call sites clear
the buffer by other sends, so this one plausibly clears the input
(Emacs's discard-input).

## 5. Selector table

The 17 selectors held code sends to a Pmacs editor (the brief's list),
plus the methods and selectors added for them.

| selector | class (stand-in) | held call site | body |
|---|---|---|---|
| `current_buffer/2`, `get_window/2`, `exception/2`, `select_buffer/2`, `insert/2`, `backward_character/1`, `show_menu/1`, `goto_beginning/1` | standard_editor | §2 | window M10, unchanged (OURS bodies; select_buffer RECONSTRUCTED-FROM-MANUAL, man15 p72, p75) |
| `mark/1` | standard_editor | my_syntax :29, my_changer :110, inwin :298 | INFERENCE (that a mark exists: RECONSTRUCTED-FROM-MANUAL) |
| `exchange_point/1` | standard_editor | my_syntax :34 | INFERENCE |
| `next_term/1` | standard_editor | my_syntax :36 | INFERENCE |
| `push_to_yank/3` | standard_editor | my_delete :48 | INFERENCE (the shared store too, from ESP overview p25) |
| `clear_input/1` | standard_editor, editor_command_interpreter | kappa2 typewin :325, REPINDEX :392 | INFERENCE |
| `cursor_with_mouse/1` | standard_editor | my_point :23 | INFERENCE |
| `two_windows/1` | standard_editor | ds_edt :1037 | INFERENCE |
| `other_window/1` | standard_editor | window.md §2.11 | INFERENCE |
| `find_file/2` | standard_editor | ds_edt :915, my_load :243 | INFERENCE (named buffers RECONSTRUCTED-FROM-MANUAL) |
| `write_file/4` | standard_editor | ds_edt :760 | INFERENCE (versions RECONSTRUCTED-FROM-MANUAL by analogy) |
| `read_with_prompt/3` | pmacs_window | ds_edt :767 | INFERENCE |
| `getl/2` | pmacs_window | kappa2 inwin :298; MENDELS init_path.esp read_string/3 (2026-11-27, psi/mendels.py) | INFERENCE (as read_with_prompt/3, §4.5: typed keys at the point, BS/DEL rub out, RETURN ends; the line is from the start of the point's line, so an old answer put there is edited) |
| `get_activate_window_count/2` | pmacs_window | ds_edt :1035 | INFERENCE |
| `exchange_window/1` | pmacs_window | ds_edt :1049 | INFERENCE |
| `view_next_screen/1`, `view_previous_screen/1` | pmacs_window (and standard_editor, OURS selectors) | window.md §2.14 | RECONSTRUCTED-FROM-MANUAL (KWIC kwod.tex) |
| `kill_region/1`, `copy_region/1`, `yank/1`, `one_window/1`, `find_file/1`, `write_file/1` | standard_editor | none (OURS selectors, §3.2 keys) | INFERENCE |
| `kill_line/1` | standard_editor | none (window M10) | OURS; since 2026-11-27 it also pushes to the yank buffer, INFERENCE |
| `push_yank/2`, `top_yank/2` | standard_editor (class) | none | OURS |
| `split/1`, `unsplit/1` | pmacs_window | none | INFERENCE (§4.7) |
| `mouse_cell/3`, `left_click/3` | pmacs_window (left_click/3 also standard_io_window, a no-op; the coordinator's second click) | none | OURS |
| `next_input/2` | editor_command_interpreter | none | OURS |
| `set_mark/1`, `set_mark_at/2`, `get_mark/2`, `move_to_cell/3`, `line_count/2`, `term_region/3` | editor_text_buffer | none | OURS |
| `redisplay/4`, `split/2`, `view_rows/5`, `set_view_top/3` | pmacs_display | none | OURS |
| `escape/3` | standard_editor (table) | none | OURS (§3.3) |

Counts for the methods added by the Pmacs reconstruction (2026-11-27), by
the label of their body (getl/2, added later the same day for MENDELS,
INFERENCE, is counted with MENDELS's stand-ins in psi/README.md):
- RECONSTRUCTED-FROM-MANUAL: 4 (view_next_screen/1 and
  view_previous_screen/1, on the window and on the editor);
- INFERENCE: 22 (mark, exchange_point, next_term, push_to_yank, two
  clear_input, cursor_with_mouse, two_windows, other_window, one_window,
  find_file/2, find_file/1, write_file/4, write_file/1, kill_region,
  copy_region, yank, read_with_prompt, get_activate_window_count,
  exchange_window, split/1, unsplit/1);
- OURS: 17 (push_yank, top_yank, escape, next_input, two left_click,
  mouse_cell, set_mark, set_mark_at, get_mark, move_to_cell, line_count,
  term_region, redisplay/4, split/2, view_rows, set_view_top).

Of the 9 held selectors that were refused before this work, the bodies
of all 9 are INFERENCE. Three of them rest in part on a manual: mark/1
(that Pmacs has a mark), find_file/2 (named buffers) and write_file/4
(versions, by analogy only). The behaviour that is RECONSTRUCTED-FROM-MANUAL
outright is the page commands (C-v, meta-V), C-n, C-p, C-x C-z, and the
`:command`/`:control_c` binding protocol.

## 6. Tests

All are in `psi/test_espc.py`, class Window, on the M10 harness. The
papyrus classes that are not loaded are OURS stubs in the harness text.

- `test_win_pmacs_syntax`: papyrus's HELD my_syntax_checker, for N = 1
  .. 4 terms (the checker stub answers error(N)). It checks the point,
  the mark and the echo line (§4.2, §4.4).
- `test_win_pmacs_delete`: HELD my_proof_deleter by its own C-c d. The
  block's text goes to the yank buffer and is deleted. Then C-p C-y
  yanks it at another place (§4.3).
- `test_win_pmacs_point`: HELD my_goal_pointer by its own mouse#l binding.
  cursor_with_mouse/1 moves the point to the cell clicked (§4.6).
- `test_win_pmacs_live`: exshow's window with the default bindings. It
  covers insert, mark, kill and yank; the `Find File:` prompt; find_file (a new
  buffer, then a buffer already visiting the file); write_file (a new
  file, then version 2 of an existing one); two views, C-x o and C-x 1.
  The frame is pinned (`M10_PINS['pmacs_edit']`) and committed as
  `../screens/pmacs_edit.png` (`winshot.py pmacs_edit`).
- `test_win_pmacs_page_and_input`: C-v twice and ESC v on 62 lines, then
  clear_input/1.
- `test_pmacs_methods_labelled` (class Standins): the labels of §0.
- The live session `psi/live_sessions/pmacs_edit.script` (test_live.py
  pins; `winshot.py pmacs_edit`) replays find, kill, yank, write and
  split from viewer key events. The mark key C-@ is Ctrl-2 or
  Ctrl-Space live (tools/simpos_live.py, OURS; test_live_keys).

Injections, OBSERVED on 2026-11-27. Each was made in a private copy of
`pim/psi` (scratch, deleted after), and the 11 Pmacs and M10 Window
tests were run on it:

| injection (stand-in) | failed (all others passed, the six M10 tests among them) |
|---|---|
| next_term/1 sets the mark at the term's start, not its end (standard_editor) | test_win_pmacs_syntax n=1, 2, 3, 4 |
| exchange_point/1 moves the point and keeps the mark | test_win_pmacs_syntax n=4 |
| push_to_yank/3 pushes nothing | test_win_pmacs_delete, test_win_pmacs_live |
| yank/1 sets no mark | test_win_pmacs_delete, test_win_pmacs_live |
| find_file/2 names the buffer after the whole pathname | test_win_pmacs_live |
| write_file/4 does not make the buffer the new file's (saved/2 dropped) | test_win_pmacs_live |
| term_region/3 starts its scan inside a comment (editor_text_buffer) | test_win_pmacs_syntax n=1, 2, 3 |
| the interpreter's clear_input/1 drops nothing (editor_command_interpreter) | test_win_pmacs_page_and_input |
| view_previous_screen/1 goes back one line, not a page (pmacs_window) | test_win_pmacs_page_and_input (the ESC v subtest) |
| mouse_cell/3 ignores the pane's top | test_win_pmacs_point row=0, row=1 (row 9 is clamped to the last line either way) |
| the upper view gets T/2 rows, not (T-1)/2 (pmacs_display) | test_win_pmacs_live |

The weak spots are these. exchange_point/1 is caught only at N = 4,
because for N <= 3 next_term/1 sets the mark again. No injection reaches
test_win_pmacs_syntax's echo line alone. cal_pmacs (test_win_m10_cal)
covers none of these methods.

## 7. Gaps only the SIMPOS manuals would settle

1. The default key table (G6). Only C-n, C-p, C-v, meta-V and C-x C-z are
   witnessed (KWIC). C-c C-h is KWIC's own binding.
2. The real meaning of next_term/1 (§4.4), and whether exchange_point/1
   and next_term/1 move by text or by parse.
3. push_to_yank/3's direction argument. Whether consecutive kills
   append. Yank-pop. How named yank buffers relate to the kill store.
4. How the mark is drawn (KWIC: "like pmacs's mark").
5. What C-x 2 splits (rows, or windows of their own) and how
   get_activate_window_count/2 counts.
6. M-x and execute_command/2 (chal INSTALL, kappa2 typewin :303). They
   need a string-to-atom conversion, and no held built-in for it has been
   identified, so they are not stood in.
7. The meta key on the PSI keyboard.
8. The `Find File:` / `Write File:` dialogue: defaults, completion, and
   the words used.
9. editor_menu/3 (cil ds_edt): extending the EDITOR MENU.
10. The lost section "Editor manual / PMACS customization / extension by
    program", which classSpec.IO2 cites.
