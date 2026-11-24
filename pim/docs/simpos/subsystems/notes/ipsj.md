# ipsj: SIMPOS sources outside the ICOT TR/TM series (IPSJ, journals, theses, FGCS, web)

Agent: ipsj. Status: COMPLETE (2026-11-24).

Layout of this file:
1. Triage.
2. SUBSYSTEM INDEX (WINDOW / LIBRARIAN / SHELL / OTHER).
3. Per-item notes:
   - IPSJ 4D series;
   - 36239, 3J-8, 7G-2;
   - 4E-7/8/9, 26580, 24478;
   - Mitsubishi Giho, FSTJ.
4. POSSIBLE SIMPOS CODE, PAGES READ, OPEN QUESTIONS, CHECKED NOTHING.


Machine-readable rows are in notes/ipsj.tsv.

Paths: lit = /Users/npe/src/living-computing/pim/docs/nonlocal/lit/ . Page = PDF page index (1-based).

## TRIAGE (step 1)

Method:
- IPSJ titles come from lit/records/ipsj/*.json (130 records).
- 31 IPSJ PDFs have no record (fetched 2026-11-23, "PSI/SIMPOS acquisition P0"); none has a text layer. Their titles were read from 300-dpi tesseract jpn OCR of page 1 (work/ipsj/ocr/), then by eye.
- Authors and topics below are as corrected after reading each item.

### IPSJ items about PSI/SIMPOS/ESP

| item (lit/ipsj/) | year | session | authors | topic | relevant? |
|---|---|---|---|---|---|
| 114006_KJ00001330812 | 1986 (33rd conv.) | 4D-1 | Chikayama, Uchida (ICOT), Ueda T. (Mitsubishi), Nakazawa (Oki) | SIMPOS programming environment: overview | YES |
| 114007_KJ00001330813 | 1986 | 4D-2 | Sato H., Shirasu, Hori A. | text editor Pmacs | YES |
| 114008_KJ00001330814 | 1986 | 4D-3 | Terasaki, Nakazawa, Touati, Chikayama | font editor | YES |
| 114009_KJ00001330815 | 1986 | 4D-4 | Kanaegami, Ishibashi (ICOT) | inspector | YES |
| 114010_KJ00001330816 | 1986 | 4D-5 | Kondo, Hagio, Ishibashi, Chikayama | ESP compiler macros | marginal (language) |
| 114011 (4D-6) | 1986 | 4D-6 | - | NOT HELD | - |
| 114012_KJ00001330818 | 1986 | 4D-7 | Kuriyama, Tomari, Ueda T., Sato H. | Japanese document processing (screenshot) | YES |
| 114013_KJ00001330819 | 1986 | 4D-8 | Azuma (東), Yokotsuka (JIPDEC), Yoshikawa (ICOT) | PSI network overview | partial |
| 114014_KJ00001330820 | 1986 | 4D-9 | Mori, Kajiyama, Azuma, Sato M. | PSI network basic functions (NCP objects) | partial |
| 114015 (4D-10) | 1986 | 4D-10 | - | NOT HELD | - |
| 114016_KJ00001330822 | 1986 | 4D-11 | Furuichi, Osaki, Azuma, Yoshikawa | file transfer, file manipulator ops | partial |
| 114017_KJ00001330823 | 1986 | 4D-12 | Yoshinaga, Kawakami, Fukui, Sato M. | printer spooler, remote print | partial |
| 36239_IPSJ-DPS86031001 | 1986-09-29 | SIG DPS 31-1 | Sato H., Chikayama, Ishibashi, Yoshida K., Uchida | SIMPOS user interface and its features (v2.50 screenshots) | YES, KEY |
| 115246_KJ00003117781 | 1988 (37th) | 4E-7 | Amanuma, Azuma, Hoshi, Tsuchikawa | network: TELNET | partial |
| 115247_KJ00003117782 | 1988 | 4E-8 | Mori, Yoshida K., Fukui, Ishihara | network: remote object access + log | partial |
| 115248_KJ00003117783 | 1988 | 4E-9 | Kajiyama, Yoshizumi, Osaki | network: FTP | partial |
| 118591_KJ00001338207 | 1990 (40th) | 7G-2 | Kato T., Sato T. (Mitsubishi Electric Computer Systems) | volume compaction (file system) | partial |
| 118681_KJ00001338298 | 1990 (40th) | 3J-8 | Kodama Yasuko, Fujimoto Seiji (Mitsubishi Electric Computer Systems) | librarian customization, menu_list | YES, KEY |
| 26580_IPSJ-OS84023001 | 1984-06-08 | SIG OS 23-1 | Hattori, Kurokawa, Sakai, Tsuji, Chikayama, Takagi, Yokoi | operating system of PSI (window mixins) | YES |
| 24478_IPSJ-ARC91091007 | 1991-11-21 | SIG ARC | Masuda, Matsumoto, Ikeda | PSI/UX architecture (SIMPOS window server on X) | YES (partial) |
| 4701_IPSJ-MGN320414 | 1991 | magazine | Kaneda, Matsuda | architecture of sequential inference machines | NO (hardware) |
| 115300_KJ00003117835 | 1988 | 2Y-5 | (AI Language Research Inst.) | Common ESP plan | marginal (language) |
| 116517_KJ00001333260 | 1989 | 3P-6 | Tanaka Y. | provisional Common ESP execution | marginal |
| 120507_KJ00001340846 | 1991 | 5M-2 | Nishiyama, Utashiro | LTB on Common ESP | marginal |

### Journals, FGCS, theses, web

| item | year | authors | topic | relevant? |
|---|---|---|---|---|
| journals/mitsubishi_giho/8609.pdf p11-16 | 1986 (Vol.60 No.9) | ?Hattori, Masuda, Kawakami, Ikeda, Nakajima | AI workstation MELCOM PSI (Fig.8 screenshot: debugger, librarian, Pmacs) | YES, KEY |
| 8609.pdf p17-20 | 1986 | Kawakami, Yoshida, Ueda, Kondo | ESP language; standard_io_window example and screenshots | YES |
| 8609.pdf other articles | 1986 | - | EXT expert shell etc. | application only |
| journals/giho_8810_8810.pdf p43-48 | 1988 (Vol.62 No.10) | Hiratsuka, Akita | software development environment (librarian pipeline, system menu figure) | YES |
| mitsubishi_giho/8907.pdf p34-35 | 1989 (Vol.63 No.7) | Ikeda, Yanada(?), Yoshinaga | PSI II, SIMPOS II B00, colour windows | YES |
| mitsubishi_giho/9106.pdf p80-87 | 1991 | Yuasa, Ueda, Matsumoto | PSI/UX overview, Table 2 environment | YES (partial) |
| mitsubishi_giho/8707.pdf p27-28 | 1987 | Akita et al. | machine translation inheriting Pmacs | application, minor |
| fstj V26_N01 p92-101 | 1990 | Tanaka J. et al. | ExReps (SIMPOS 4.2 status line in screenshots) | partial |
| journals/jstage-wincs_wincs_8_1_54.pdf | 1991 (Computer Software 8(1)) | Imanaka, Fujimoto, Uehara, Toyoda | WINCS: synthesizing window classes on SIMPOS (~40 window classes, nature lists) | YES, KEY |
| fgcs/1984/FGCS84en-proc/84eRandD-5 | 1984 | Yokoi, Uchida | SIM programming and operating system | = ICOT TR-087 (TR series, out of scope) |
| fgcs/1984/FGCS84en-proc/84eRandD-4, 84eLPLM1-4 | 1984 | Uchida; Chikayama | SIM progress report (= TR-086); Unique features of ESP (= TM-055) | TR/TM series, out of scope |
| fgcs/1984/FGCS84en-proc/84eANGC2-1, 84eANGC2-2 | 1984 | Taki; Yokota | PSI hardware; PSI microinterpreter | NO (no UI) |
| theses/ (Nakashima, Ohno, Rokusawa) | - | - | PSI hardware / parallel | NO |
| web/ (23 pages mention SIMPOS) | - | - | museum/history prose; CiNii manual records | leads only |

### IPSJ items NOT about SIMPOS (checked by title / p1 OCR)
- CHI (NEC Prolog machine): 113874-113877, 117734, 118850, 24733, 31144.
- Toshiba AI chip IP1704: ipsj_116851, ipsj_117919, ipsj_24651, ipsj_59748.
- Multi-PSI hardware/network: 113878, 113879, 113880-113883, 15329, 24868, 24765.
- PIM / KL1 / PIMOS / GC (all 100+ remaining records): not SIMPOS. 115119 "SHELL on PIMOS" is PIMOS's shell, not SIMPOS.
- PSI hardware/firmware: 15436, 15461, 15599 (PSI GC), 31384 (PSI micro-interpreter), 115306, 24746, 24677.

## SUBSYSTEM INDEX (the strongest facts, by subsystem; details and citations are in the per-item notes below)

Citation keys:
- IPSJ items are cited by lit/ipsj file-number prefix (e.g. 36239 p5).
- Giho = Mitsubishi Denki Giho, cited by issue (8609 = Vol.60 No.9, Sep 1986).

Version map used for the tags:
- 1984-06 = pre-release
- Apr 1986 = 2.0
- Sep 1986 = 2.50 (printed on screen)
- 1988-90 = 4.x-5.x
- 1989 Mitsubishi "SIMPOS II B00"
- 1991 PSI/UX

### WINDOW
- **Window classes, 1984** (26580 p7-8, PRINTED, pre-1.0): `bare_window`, `with_border`, `with_label`, `window_with_border_and_label`. `with_border` follows the TM-061 variant (not TM-065).
- **`standard_io_window` API, Apr 1986** (Giho 8609 p19-20; PRINTED code + PROSE):
  - create/3 class method, with options `size(W,H)`, `position(X,Y)`, `title(Str)`;
  - instance methods activate/1, select/1, putl/2, gett/2, set_position/3, putc/2.
- **`#window` API, Sep 1986** (36239 p5 SCREENSHOT, application code in a Pmacs buffer):
  - create/3 with `size(manipulator)` and `position(manipulator)`;
  - erase_cursor/1, set_inside_units/3, activate/1, refresh/1, get_inside_size/3, get_mouse_position/3;
  - draw_rectangle/8 `(W,X,Y,W,H,1,filled,exclusive_or)`.
- **`window` instance slots, v2.50** (36239 p6, inspector SCREENSHOT): `dependency`, `echo_buffer` ($list), `employers` ($extensive_list), `error_report_window`, `error_status`, `exposed_flag` (list cut off).
- **UI rules, 1986** (36239 p4 PROSE):
  - every character-I/O window is a "window with Pmacs function" (all character I/O from 3.0, 4D-2);
  - two menu kinds: fixed-length operation menus and variable-length object menus.
- **Screen chrome, 1986** (Giho 8609 p16/p20, 36239 p5-7; SCREENSHOT): the bottom status line holds:
  - `USER : <user>`, plus `SIMPOS Version 2.50` (Sept);
  - inverse boxes `screen` / the name of the window under the mouse / `spool`;
  - the date as `DD-Mon-YY Weekday hh:mm:ss`.
- **Status line in Sep 1989** (FSTJ 26(1) p99 SCREENSHOT): `USER : demo` / `SIMPOS Version 4.2`; `screen` / `editor_buffer_window/19`; `SWAPPED`, `spool`; `12-Sep-89 Tuesday 10:25:41`. The 1986 layout persists into 4.2.
- **Window mixin classes, ~1989** (WINCS, PRINTED and PROSE): about 40 window classes.
  - Base classes: `inferior_window`, `popup_window`, `temporary_window` (one is mandatory).
  - Function mixins: `as_output`, `as_input`, `as_input_buffer`, `as_graphics`, `as_markers`, `as_scroll`, `as_menu`, `as_single_select`, `as_mouse_input`, `as_superior`; also `shared_window`.
  - Sash mixins: `with_border`, `with_label`, `with_margin`.
  - Order: `with_*` first, the base class last.
  - Constraints: `as_menu` needs `as_mouse_input`; `as_menu` excludes `as_graphics`; `with_label` comes before `inferior_window`.
  - Methods: `as_graphics` draw_line/5 and draw_circle/7.
- **Window labels, 1986** (SCREENSHOT):
  - `debugger_1`, `librarian_1`, `pmacs_1`, `pmacs_4`, `Debugger_4`, `Inspector`;
  - `editor_main_window/5` (4D-7), `mt_utility_window/3`, `talk_input_window/?`.
- **Fonts** (4D-3, PROSE):
  - font file = header / index / pattern, up to 65,536 characters;
  - the window subsystem makes **font objects** from font files;
  - icons are drawn with the font editor.
- **Font editor** (4D-3 / 36239, SCREENSHOT):
  - select mode menu EXIT/LOAD/SAVE/ATTRBT/EDIT;
  - pattern mode commands Draw, Draw Line, Clear, Move, Set Sample, Real Size, Circle, Scale, Add, Swap, Reflect, Box, Cut;
  - pen black/white/inverse, dot/line/square; Char mode; Help; Width/Height/Bias.
- **Window manipulator**: changes a window's position, size and state by mouse (36239 PROSE; Giho 9106 Table 2).
- **Colour windows**, SIMPOS II B00, 1989 (Giho 8907 PROSE): colour palette of colour pairs; colours given by colour number; one pair = monochrome window; palette shared parent-to-child.
- **PSI/UX 1991**: the SIMPOS screen lives inside one X window; SIMPOS window manager + window server (X client) (24478, Giho 9106).

### VARIANTS against held code (required/requirements.tsv; arity counts the receiver)

| fact (source, year) | held programs | verdict |
|---|---|---|
| window draw_rectangle/8 `(W,X,Y,W,H,1,filled,exclusive_or)` (36239, 1986) | draw_rectangle/8 on {as_graphics, inferior_window}; standard_io_window draw_rectangle/5 and /7 | MATCH on the as_graphics mixin; VARIANT on standard_io_window |
| as_graphics draw_line/5 (WINCS, 1989) | standard_io_window draw_line/7 and /8 | VARIANT (WINCS may abbreviate) |
| standard_io_window create/3, activate/1, putl/2, gett/2 (Giho 8609, 1986) | the same class and arity | MATCH |
| standard_io_window set_position/3 (Giho 8609) | set_position/3 on inferior_window, standard_superior_window | VARIANT of class (the method is in the mixins) |
| standard_io_window putc/2, select/1 (Giho 8609) | putc/2 on pmacs_window and standard_io_buffer; select/1 unattributed | not attributed in held programs |
| window erase_cursor/1, set_inside_units/3, get_inside_size/3, get_mouse_position/3 (36239) | present on window nature sets (as_graphics, as_markers, as_mouse_input, ...) | MATCH as mixin methods |
| window refresh/1; as_demo_program initiation_end/1 (36239) | absent | ABSENT |
| process create/2, activate/2 (Giho 8609) | the same | MATCH; set_sub_priority/2 is only unattributed |
| network connect/send/receive (Giho 8907) | arity 2 on port / channel | class unknown |
| Nature ORDER with_* ... as_* ... inferior_window (WINCS Fig.5, 1989) | the same shape, e.g. {with_superior_input_buffer, with_border, as_output, as_graphics, as_markers, as_mouse_input, inferior_window} | MATCH |

### LIBRARIAN
- **Menus by version**:

  | version | menu | grade, source |
  |---|---|---|
  | Apr 1986 (~2.0) | `librarian_1`: Check, Catalogue, Compile, Uncompile, Save, Load, Delete, Execute (rest hidden) | SCREENSHOT, Giho 8609 p16 |
  | Sep 1986 (v2.50) | same + **Utility** | SCREENSHOT, 36239 p5 |
  | 1990 (v5.x) | `librarian 48/49 (default: user)`: Set up, Check, Catalogue, Save, Load, Delete, Package, Execute, Utility, ESP tool, [Close], with submenus `set_up_menu` and `package` | SCREENSHOT, 3J-8 Fig.1 |

- **Menu definition file**: the `menu_list` in the librarian initialization file, as printed in 3J-8 Fig.2 (PRINTED, v5.0). Command names: set_up, save_state, check_menu_item, check, catalogue, save, load, delete, abolish, forget, delete_resource, up.
- **Transcript format** (SCREENSHOT, 1986):
  - `File Name>` prompt, then `Catalogging "<file>"...` (sic);
  - each class indented, then `<class> end.`;
  - `<class> auto loaded.` when a needed class is loaded automatically;
  - `Class Name>[default]`.
  - The CLASS NAME popup has DO IT, EXIT, ALL BUT SELCTED (sic), FROM WHITE BOARD, then class names.
- **Model** (PROSE: 36239, Giho 8810, 3J-8):
  - library = registry of all classes, and packages from 5.0;
  - compiler: source -> class template; "object composer" (linkage editor) + "program base" -> class object;
  - interpreted vs compiled code is selectable per class;
  - template save/load; batch commands.
  - Librarian = command execution part + program interface part + I/O part. Customization arrived in 5.0; 6.0 was in development in 1990.

### SHELL / system menu / debugger
- **SYSTEM MENU, v2.50, Sep 1986** (36239 p4 SCREENSHOT):
  - EXPERTS: Debugger, Pmacs, File, Librarian, Font_editor, Edips, Spooler, plus user demos;
  - MEDIA SYSTEMS: user process list, window manipulator, network, shell, whiteboard, kanakan initiate, garbage collection, login, shut down.
  - VARIANT vs TM-181 p3.
  - EXPERTS run as many instances; MEDIA SYSTEMS run as one only. Users can add to EXPERTS.
- **Login init** (36239 PROSE): system-menu items, directory logical names, default directory, an initial program, auto-created PSs and their window positions.
- **Coordinator and shell share one cell** in the 1986 structure figure (36239 Fig.2-1).
- **Debugger** (Giho 8609 p16 SCREENSHOT, Apr 1986):
  - menu Method / Step / Skip / Leap / Fail / Retry / No trace / PREDICATE / clause;
  - trace format `(n)d CALL|EXIT [builtin>|new>|]> goal ? step`; the 36239 trace also shows the ports `unify>` and `pick>`;
  - a `Variable` pane; the top level is `?-`; results print as `Var= value`; an instance prints as `$class`; a class object is `#class`.
- **Inspector** (36239 SCREENSHOT): command pane exit / parameters / break / from_WB; `Memory` pane; objects print as `$class@1:hex`.
- **Process** (Giho 8609 p16 SCREENSHOT, application code): `:create(#process,P)`, `:set_sub_priority(P,2)`, `:activate(P,Program)`.
- **GC can be forced from the system menu** (Giho 9106 PROSE; 36239 shows "garbage collection").
- **User management**: users are registered; `>sys>user>NAME` home directories (SCREENSHOT); remote users are written `node!user` and a superuser exists (4E-8 PRINTED).

### OTHER (Pmacs, file system, manipulators, network)
- **Pmacs**:
  - gap buffer and buffer pool; over 100 commands;
  - keyboard and program macros (an `editor` object, replaceable by a user's subclass);
  - "window with Pmacs function";
  - mode line `PMACS(esp)[l,c] *-n* FILE.EXT.v --n%--`;
  - EDITOR MENU: ABORT, List Buffers, Save All Files, Set Font, Set Echo Font, Set Window Size, From Whiteboard, To Whiteboard (36239);
  - KANAKAN popup.
- **File manipulator popup** (36239 SCREENSHOT): delete, rename, copy, copy to fdd, append, describe, type, dump, word count, pattern search, to whiteboard.
- **Spooler manipulator** (36239 SCREENSHOT): Direct, Spool, Test, Manipulate?, Cancel, EXIT.
- **MT utility menu** (36239 SCREENSHOT): initialize volume, show volume label, show file label, save to MT, restore from MT, attribute, exit.
- **Paths**: `node::>sys>user>name>file.ext.version`. File system: Unix-like tree, 4 KB blocks, a "file file" (7G-2).
- **Network**:
  - LIA/NCP objects node/socket/cable/plug (4D-9);
  - file server protocol open/make/close/dispose/read/write (4D-11);
  - NETCP DIR/DEL/XMT/RCV-REQ;
  - print classes `virtual_printer`, `printer_spooler`, `as_spooler` (4D-12);
  - TELNET over `tcpip_socket` with a window folder (4E-7);
  - FTP `FTP>` and menu modes (4E-9);
  - TALK windows `TALK INPUT` / `TALK OUTPUT` with BYE / MODE (36239).

## PER-ITEM NOTES (step 2). All Japanese -> English is TRANSLATION (mine) unless quoted.

### 4D-1 (114006) "SIMPOS programming environment: Overview" (SIMPOSのプログラミング環境 -- 概要)
Chikayama T., Uchida S. (ICOT), Ueda Takasumi (Mitsubishi), Nakazawa O. (Oki). IPSJ 33rd conv. (autumn 1986) pp.407-408. Eyed p1-p2 at 150 dpi (half of 300 dpi render).
- Version history (PROSE, TRANSLATION, p1 sec 2): ICOT founded Jun 1982; KL0 designed first; first PSI hardware end 1983; firmware "roughly complete" spring 1984; SIMPOS demonstrated at FGCS'84 (Nov 1984), self-compiler not yet running; **v0.7 end 1984, v1.0 spring 1985, v1.5 summer 1985, v2.0 spring 1986, v2.5 summer 1986**; p2 sec 7: **version 3 ("第3版") due end of 1986**, goals: unify the user interfaces of the subsystems, which had been inconsistent, and tidy the system grown complex by repeated changes.
- Size (PROSE, p1): about **200,000 lines of ESP source, about 1,500 classes, about 18,000 predicate definitions** (1986).
- User-visible features (PROSE, p1 sec 3, TRANSLATION):
  - (1) open OS: written wholly in ESP; applications use OS functions freely via inheritance.
  - (2) man-machine interface: easily customized multi-window system (マルチウィンドウ・システム); rich menus; windows "with PMACS function" (PMACS機能付きウィンドウ); the parts used to build SIMPOS are open to users; a **font editor** using the bitmap screen and mouse edits character fonts **and icons**; a **WYSIWYG document processing system**.
  - (3) program development: compiler with powerful macros; **librarian** (ライブラリアン) to manage programs; **debugger** capable of symbolic step execution; **inspector** (インスペクタ) for complex data structures; **call counter** (コール・カウンタ) for run-time behaviour.
  - (4) network: file server, print server, mail server, file transfer PSI-PSI and with general-purpose machines.
- Performance (PROSE, p2 sec 6): PSI ~40 KLIPS; smallest loop iteration at least 25 us; PSI-II expected 3x. The first SIMPOS took "several seconds" to display one character; in about 3 months speed rose two orders of magnitude (3x of it from firmware support); firmware supports measuring dynamic predicate call frequency.
- p2 sec 4: all levels (process, memory, I/O device management up to UI) in one language ESP; users define objects inheriting OS function and extending/modifying it ("open OS").

### 4D-2 (114007) "... Text editor Pmacs" (テキスト・エディタ Pmacs)
Sato Hiroyuki (ICOT), Shirasu Hiroyuki (AIC), Hori Atsushi (MRI). pp.409-410. Eyed p1-p2.
- Spelled **"Pmacs"** throughout this paper (4D-1 writes "PMACS").
- Features (PROSE, TRANSLATION, sec 2): emacs-like; **over 100 commands**: editing by character, word, line, page; comment handling; upper/lower case conversion; paren matching; narrowing ("編集範囲の局所化", localising the edit range); **auto-save**.
- Text held in **buffers**; all buffers registered in the **buffer pool** (バッファ・プール) and accessible **by buffer name from any SIMPOS process** (sec 3). Several Pmacs processes may edit one buffer; one Pmacs may edit several buffers; user programs may create a buffer, insert text, and view it with Pmacs. Fig.1 (figure): Pmacs-1..Pmacs-N and a user process each pointing at buffer-1..buffer-N inside a dotted box "buffer pool".
- Redisplay: optimised, reuses on-screen data by transfer, rewrites only needed parts by ordinary character output; **a typed command interrupts redisplay** (command takes priority).
- **Kana-kanji conversion**: SIMPOS's kana-kanji conversion sits in the **keyboard handler** (キーボード・ハンドラ, lowest layer) so all programs get it (sec 4); Pmacs adds word-processor-style input: converts a specified region of romaji in the buffer to kanji/kana, either while typing or later over a mouse-marked region; two selection modes "sequential selection" (逐次選択) and "batch selection" (一括選択), user-selectable; candidates shown one by one as "next candidate" (次候補) or all at once in a menu.
- Customization (sec 5): **state variables** (状態変数), e.g. "distinguish case in string search?"; **keyboard macros** (example: move to end of line, insert ".", move to next line, bound to one key); **program macros**: user defines commands in ESP.
- Fig.2 buffer structure (PRINTED figure): text "line1 LF line2 LF" with indices 0..11; LF stored as a character; implementation is a **gap buffer**: current position (CP, shown as the cursor) with a gap right of CP; insert fills the gap, delete widens it, cursor motion moves the gap; gap exhausted -> buffer auto-extended and new gap made.
- Fig.3 program macro implementation (PRINTED figure): "Pmacs command interpreter" sends a **message** to an "**editor** object with editing functions"; replacing it with a user's **editor'** with added commands gives user-defined commands; ESP inheritance lets a user take all standard Pmacs functions or drop unneeded ones. INFERENCE: ancestor of held `standard_editor` / `pmacs_window`.
- Sec 6 **"Window with Pmacs function"** (Pmacs機能付きウィンドウ): system output and input echo-back are inserted into a buffer; while typing, the user may re-use earlier input or system output with Pmacs editing commands; system-specific commands for this window added by program macro. "From SIMPOS 3.0, every programming system that outputs characters uses this window", so all character I/O commands are processed by Pmacs (PROSE). INFERENCE: ancestor of `standard_io_window` (TM-181 p3).
- Sec 7: Pmacs **released to users in SIMPOS 2.0**; in progress: Japanese input, macros, the Pmacs window, command extensions.

### 4D-3 (114008) "... Font editor" (フォントエディタ)
Terasaki Rimiko, Nakazawa O. (Oki), Herve Touati (INRIA), Chikayama T. (ICOT). pp.411-412. Eyed p1-p2; figures zoomed at 300 dpi.
- Window system outputs characters to a window (called a "logical terminal") by char-code lookup in a **font** (PROSE). The **SIMPOS window subsystem** manages fonts: reads system- or user-defined font information from **disk files**, creates **font objects** (フォントオブジェクト) usable by windows, gives the font editor an interface to font files (sec 2). Fig.1: user -> window (font object setting); user -> font management (font object) <-> font file; user -> font editor ("data format conversion").
- **Font file format** (PROSE, sec 2): variable-length binary file in three parts: (1) **header**: parameters common to all characters, e.g. number of characters; (2) **index**: per-character table: char code -> position and size of its image in the pattern part, etc.; (3) **pattern**: all bit patterns together. **Max 65,536 characters**; kanji fonts handled.
- Two modes (sec 3): **character selection mode** (文字選択モード) and **pattern edit mode** (パターン編集モード).
- Fig.2 (SCREENSHOT, eyed at 300 dpi): selection-mode screen: grid of 22 columns headed 2C..41 (hex, JIS 2nd byte) x 20 rows 3C..4F (JIS 1st byte), cells showing kanji; right column: scroll arrows "< ^ > v"; menu **EXIT / LOAD / SAVE / ATTRBT / EDIT**; below, a box showing the selected character (新) large.
  Functions: register/delete characters; select a character for pattern edit; change all-character parameters; load/save font files on disk; header and index updated on edit.
- Pattern edit mode (sec 3.2; Fig.3 SCREENSHOT, eyed, zoomed 3x): enlarged dot grid with a row of boxes along the top; right-hand panel, top to bottom:
  - pen: **black** (highlighted) / **white** / **inverse**; **dot** (highlighted) / **line** / **square**
  - **Char mode**, **Help**
  - commands: **Draw, Draw Line, Clear, Move, Set Sample, Real Size, Circle, Scale, Add, Swap, Reflect, Box, Cut**
  - **Width 2? (26 or 28, blurred), Height 24, Bias 0**
  - real-size sample of the character.
- Functions (PROSE): (1) draw by mouse (pen or eraser; tips dot, line, square); line by endpoints; circle by centre+radius; (2) character size = a rectangle on the display, resized by mouse; (3) grid magnification; (4) real-size image; (5) translate and mirror; (6) **character pattern register** (temporary store for part of a pattern); (7) **two patterns at once**, black (main) and grey; **SWAP** and **ADD**; Fig.4 composes 持 from 扌 and 寺.
- Pattern passed back to selection mode and assigned to a char code -> registered in that font.
- **Font editor public to PSI users from SIMPOS 2.0** (sec 4). Cites Iima et al., IPSJ 29th conv. (autumn 1984) **4E-6 "SIMPOS window subsystem"** (SIMPOSのウインドウサブシステム) -- NOT HELD (lead).

### 4D-4 (114009) "... Inspector" (インスペクター)
Kanaegami Atsushi, Ishibashi Hiroyoshi (ICOT). pp.413-414. Eyed p1-p2.
- Purpose (PROSE, TRANSLATION): debugger shows the logical flow; **inspector** (インスペクタ) shows object state changes; the two are complementary. Inspector analyses objects (shows each **slot name and value**) and **KL0 data** (structured data e.g. vectors: shows elements). Each datum shown with its type and attributes; structured data's elements shown **as a menu**; selecting an element with the mouse descends into it.
- Example: SIMPOS **list object** (リスト・オブジェクト, stores data as a queue, used for control and resource management). Three views (sec 4):
  1. **as queue**: all stored data in order, structure hidden (most used; specially supported for list objects). Fig.1: data5 -> [data4|data3|data2] -> data1.
  2. **as object**: slot names and values. **List object has two slots, first entry and last entry; each entry is an entry object (エントリ・オブジェクト) with a slot for the data and a slot for the next entry** (Fig.2, PRINTED figure: list object slots `first:`, `last:`; entry object slots `next:`, `object:`; last entry's next points back to the list object).
  3. **as structure (vector)**: on PSI an object is a heap vector holding slot values plus a pointer to an **object descriptor** (オブジェクト記述子) which points to the **method table** (method names) and the **slot table** (Fig.3: slot table rows `object`,1,`next`,2 -- i.e. slot name -> index). Creating a list object allocates only the vector marked *. Method-table view lets one see the code registered there ("very special users only").
- Also mentions **hash index** objects (ハッシュ・インデックス) whose contents can be listed by view 1 without knowing hash values.
- Version: 1986 (SIMPOS 2.x). Class `inspector` is in partition_other (A-tier).
- INFERENCE: slot names `first`/`last` of the list object and `next`/`object` of its entry are a candidate for `list` internals (held `list` class has 20 instance methods per requirements).

### 4D-5 (114010) "... Extended features of the ESP compiler" (コンパイラの拡張機能)
Kondo Seiichi (Mitsubishi), Hagio Genichiro (Beacon System), Ishibashi H., Chikayama T. (ICOT). pp.415-416. Eyed p1-p2. ESP language, not UI; summary only.
- Class definition skeleton (Fig.1, PRINTED): `class <name> has <class part> instance <instance part> local <local part> end.` Parts are `;`-terminated clause sequences.
- **Clause-level macro** (PRINTED syntax): `<pattern> => <expansion> when <generating goals> where <checking goals> with <added clauses> :- <expansion condition>`. Example (PRINTED): `X + Y => Z when add(X,Y,Z);` expands `p(X,Y) :- q(X+Y);` to `p(X,Y) :- add(X,Y,Z), q(Z);`; in head position the generating goal goes to the body end. `with` example `some(X in List, Condition, Tail)` -> dummy predicate with added clauses; macros can generate unique atoms to name generated predicates.
- **Class-definition-level macro**: `<pattern> ==> <expansion> with <added clauses> :- <condition>`; example `(Functor <- List) ==> Expanded :- convert(List,Functor,Expanded);` so `author <- [kondoh,hagio,ishibashi,chikayama]` gives 4 clauses.
- **Macro bank** (Fig.5 PRINTED): `macro_bank <name> has nature <inherited macro banks>; <macro defs> local <local defs> end.` Multiple inheritance of macro banks; local predicates; unconditional insertion of clauses into class/instance/local parts. If a class names no macro bank, the compiler's **standard macro bank** is used; every macro bank inherits it automatically. Users may also add/change operators. DCG can be built with these macros. (Already covered by layers/ESP.md presumably; cross-check.)

### 4D-7 (114012) "... Document processing" (文書処理)
Kuriyama Ken (Gakken), Tomari Yoichiro, Ueda Takasumi (Mitsubishi), Sato Hiroyuki (ICOT). pp.419-420. Eyed p1-p2, screenshot zoomed at 300 dpi (bottom 45% crop).
- PSI internal character code is **16-bit (JIS C 6226)**; kana/kanji used like alphanumerics; outputs: bitmap display, kanji printer, laser printer (PROSE).
- Japanese document system: WYSIWYG; four functions (Fig.1 tree): **TEXT file creation** (all input via Pmacs), **layout** (paper size, writing direction, left/top margins, columns; per-page regions set by mouse, each region gets a TEXT file and format), **edit** (flows TEXT into the layout, writes intermediate **PIF (Print Image File)**; line-head/line-end kinsoku rules), **output** (reads PIF, shows a page on the bitmap display, or prints on the kanji printer; A4 portrait cannot fit the screen so scrolling by bit-image transfer).
- Correction: text selected by mouse in the display window is sent to a **Pmacs window created inside the document system** for correction.
- **Fig.2 SCREENSHOT "display screen: TEXT correction"** (eyed): one large frame; left column headed **メニュー (Menu)** with items **ページ (Page)**, **TEXT**, **プリント (Print)**, and at the bottom **終了 (Exit/Quit)**; right area headed **表示 (Display)** showing a laid-out 2-column page (the page being typeset is itself a manual for kana-kanji input, see below); below it an embedded Pmacs window whose **label bar reads `editor_main_window/5`**, containing the text, then a **mode line `PMACS(esp)[62,4] Pif_editor  --Top--`**, then an empty one-line area (INFERENCE: minibuffer/echo area); a further empty strip at the bottom of the frame.
  - INFERENCE: the label format `<class-or-name>/<n>` matches window labels of the form name/instance-number; `editor_main_window` is a held simpos## class (partition_window, A-tier, 1 class + 8 instance methods). Mode line fields: editor name, mode `(esp)`, `[62,4]` (INFERENCE: position, e.g. line/column or buffer number), buffer name `Pif_editor`, `--Top--` scroll position (emacs style).
- Text visible inside the screenshot page (SCREENSHOT, a document typeset as the example; content TRANSLATION): "kana-kanji input ... in simpos the kana-kanji conversion is built into the system, as a routine in the core of simpos, not done by a particular application ... the keyboard switches from the normal alphanumeric input mode to kana-kanji input mode by an input-mode switch instruction ... so every program that requests keyboard input can input kana-kanji data"; section "2.1 starting the kana-kanji system: (1) **KANAKAN_INITIATE** -- loads the dictionary and fonts needed by kana-kanji conversion and allocates buffers; must be started before kana-kanji conversion". Bunsetsu (phrase) conversion: romaji typed per phrase, grammar analysis picks the kanji part.
  - KANAKAN_INITIATE: a SIMPOS command/program name (SCREENSHOT, version 1986). Not in requirements as far as I know (OPEN).
- Cites Fujimaki, Kuriyama, Ueda, Tsuji, "SIMPOS programming system -- kana-kanji conversion", IPSJ 30th conv. (spring 1985) -- NOT HELD (lead).

### 4D-8 (114013) "... Overview of the PSI network system" (PSIネットワークシステムの概要)
Azuma Yoshiro, Yokotsuka M. (JIPDEC), Yoshikawa Sadayuki (ICOT). pp.421-422. Eyed p1-p2.
- 1986 status: **18 sites, 21 LANs, about 60 hosts** (mainly PSI, also DEC VAX-11) (PROSE).
- Hardware: LIA (LAN interface adapter; LIA protocol: 1:n connection and connectionless, 2-phase-commit "commitment mode"; full duplex, transparent; **1400 bytes per packet**), LIB (IEEE-488 board in the host), NCLIA (network console: diagnostics, configuration, logs; gives config info to hosts), BRG (bridge), GW (gateway over DDX packet network), TC (transceiver), H (host). Fig.1 topology.
- Software (Fig.2 "software configuration overview", eyed; PSIi user side, PSIj server side, each with an **NCP** box):
  - basic: NCP = **user-interface objects + manager process + LIB handler process**.
  - **File server system**: user side `AP (editor) etc.` with a **net file object** (ネットファイルオブジェクト); **net file manipulator** (ネットファイル・マニピュレータ) with a net file object; server side **net file server** (ネットファイルサーバ) and a **spawn server** (スポーンサーバ).
  - **Print server system**: `AP` with **net print object**, **net print file**, **net print user process**; **net print manipulator**; server side **net print server** and **printer system** with spool file.
  - **Heterogeneous file transfer**: **NETCP** user and **NETCP server**.
  - **Talk system**: talk (input) / (output) windows both sides, each to the BMD (bitmap display).
  - **Mail server system**: **mail user** <-> **mail server** with mailbox.
  - All user-side boxes connect to **BMD**.
- Application functions (PROSE): operate other PSIs' file directories like the own PSI's; PSI-VAX file transfer and remote directory listing; print a file on another PSI's printer like one's own; e-mail and **electronic bulletin board** between PSI users; **talk**: real-time terminal-to-terminal between 2 PSIs, and **display list of PSIs on the net and their users** (PROSE).
- Future: integrate network functions into the PSI OS.

### 4D-9 (114014) "... Basic functions of the PSI network system" (PSIネットワークシステムの基本機能)
Mori Takeshi (Oki), Kajiyama Takuya (AI Co.), Azuma Y. (JIPDEC), Sato Masatoshi (ICOT). pp.423-424. Eyed p1-p2.
- NCP written in ESP; LIA protocol represented by objects (PROSE, sec 4.1): **node object** (a host; holds its machine address in the network), **socket object** (origin for forming a communication group at a node; several per node, each with a node-unique id; logical circuits run socket-to-socket; manages its virtual-circuit objects), **cable object** (a logical circuit; does NCP internal processing/state for real communication; between socket pairs; several per socket), **plug object** (the **user interface of NCP**: carries requests/responses between user process and NCP processes; each plug has a **receive queue**; user takes messages per cable or per plug in arrival order). Fig.1: node > socket > plug; cable between sockets; user process operates the plug.
- NCP processes (sec 4.2, Fig.2): **network manager process**, **LIB handler process**, **network timer process**; all talk by a common message called **network message**. Manager turns plug requests into **LIA command objects** sent to the LIB handler; most processing is written in the cable. Only sessions (2-party groups) supported in 1986; connectionless being added. Cites Takayama et al., IPSJ 29th conv. 4E-7 (1984) -- NOT HELD.
- Classes node/socket/plug/cable are also in TR-055/TR-057 (STRUCTURE s8); this paper gives their 1986 roles.

### 4D-11 (114016) "... File transfer" (ファイル転送機能)
Furuichi Masakazu (Mitsubishi), Osaki Hiroshi, Azuma Y. (JIPDEC), Yoshikawa S. (ICOT). pp.427-428. Eyed p1-p2.
- Three functions: (1) **remote file access** (create/read/write/delete any PSI's files with the same interface as local files); (2) **file operation** via the file manipulator on any machine's directories/files (copy, merge, reference, print); (3) heterogeneous file transfer (PSI-VAX; also usable PSI-PSI).
- **File server protocol**: request command per SIMPOS file-system method, so remote files use the same method calls. Request commands (PRINTED table, TRANSLATION of meanings):

  | cmd | meaning |
  |---|---|
  | open | open the named file, return its management info as the reply |
  | make | as open, but first create a new file with the given pathname |
  | close | close the file |
  | dispose | delete the file |
  | read | read `length` from given position, transfer contents |
  | write | write data from given position onward |

  Fig.1: on PSI#1 the **file manipulator** (ファイル・マニピュレータ) and a **user process** each hold a **file object**; PSI#2 runs a **file server process**; link = "PSI net basic function" + "file server protocol".
- **NETCP protocol** (heterogeneous): request commands **DIR-REQ** (get directory info), **DEL-REQ** (delete file), **XMT-REQ** (user->server transfer; server creates file), **RCV-REQ** (server->user; server opens file and starts transfer). Fig.2: NETCP process (PSI#1) <-> NETCP server process (VAX/PSI#2).
- Applications (sec 4): (1) **editors (PMACS, EDIPS)** use remote file access: edit a file on another PSI exactly like a local one; (2) **NETCP (NETwork file CoPy system)**: directory listing, copy, delete between PSI/VAX; needs a program on the VAX; **all operations typed as commands from the keyboard**; **wildcards** operate on many files at once; (3) **file manipulator**: UI to directories/files using remote access, heterogeneous transfer and file operations; operating another PSI's directory exactly as one's own. File-manipulator operations (PRINTED table, TRANSLATION):

  | op | meaning |
  |---|---|
  | delete | delete the file |
  | copy | copy the file |
  | rename | change the file name |
  | describe | show creation date, creator name, etc. |
  | type | output file contents to a window or printer |
  | dump | output contents in hexadecimal |
  | append | merge files |

- Measured (PRINTED table): 100 KB file: same machine PSI 13 s, VAX 3 s; PSI->VAX 35 s, VAX->PSI 50 s, PSI->PSI 52 s. Before, VAX->PSI over RS-232C took ~480 s.
- Future: VAX remote file access; build network into the SIMPOS file system.

### 4D-12 (114017) "... Printer spooler and remote print" (プリンタ・スプーラ機能とリモート・プリント機能)
Yoshinaga Toshiro, Kawakami Takato (Mitsubishi), Fukui Hirotaka (JIPDEC), Sato Masatoshi (ICOT). pp.429-430. Eyed p1-p2.
- Classes/objects (PROSE + PRINTED figure labels, version 2.5 1986):
  - **`virtual_printer`** ("virtual _printer" in print): the object a user prints to; user allocates an instance to its own process; internally opens a **spool file**, writes data, on close sends a message (spool-file name, destination, ...) to the spooler process.
  - **`printer_spooler`**: object doing output to the printer device; defines only the output method; general spooling is in **`as_spooler`**, which it inherits; to spool a new device, inherit `as_spooler` and define its output method.
  - Fig.1: user process (virtual_printer) -> message -> spooler process (printer_spooler containing **printer** and **laser_printer**); spool file; **management file** (管理ファイル).
  - Spooler process runs at low priority; writes each job to the management file on receipt, so jobs survive shutdown and restart at next boot.
- **Spooler manipulator** (スプーラ・マニピュレータ) functions (PROSE list, TRANSLATION): (1) switch **spool mode / direct mode**; (2) **test print**; (3) **cancel** the spool file being printed; (4) operate queued spool files (**delete, show/change output parameters, change output order**). Uses the **window system** as I/O; all by **mouse** only.
- **Remote printer** (SIMPOS **2.5**): user gives `virtual_printer` the **node name** of the other PSI; internally a **net print file** is made, a **net print send process** (ネットプリント送信プロセス) opens a logical circuit, a **net print receive process** (受信プロセス) on the other PSI receives into a spool file and messages the spooler process like a local `virtual_printer`. **Net print management file** on the sending side so nothing is lost on shutdown. Built on 4D-8/4D-11 file transfer.
- Held classes: `printer`, `laser_printer` (partition_other A-tier). `virtual_printer`, `printer_spooler`, `as_spooler` NOT in the partitions (INFERENCE: renamed or unused by held programs).

### SIG-DPS 31-1 (36239) "SIMPOS (OS of the sequential inference machine PSI) -- user interface and its features" (ユーザ・インタフェースとその特徴)  **KEY SOURCE**
Sato Hiroyuki, Chikayama T., Ishibashi H., Yoshida Kaoru, Uchida S. (ICOT). IPSJ SIG Multimedia Comm. & Distributed Processing, 1986-09-29, 8 pp. All 8 pages eyed at 150 dpi; every screenshot re-rendered at 600 dpi and read by eye. Screenshots are dated **08-Sep-86 Monday**, status line **"SIMPOS Version 2.50"**, user **hiroyuki**, node **i3psi7** (INFERENCE from pathnames).

General (PROSE, p1, p8): SIMPOS development began **May 1983**; ~40 people working toward 3.0; >200k lines; PSI to exceed 100 units this fiscal year. Timeline table p8 (PRINTED): 1982/6 ICOT lab founded, KL0 design; 83/5 SIMPOS group formed; 83/12 first PSI delivered; 84/3 firmware roughly complete; 84/11 FGCS'84 demo version (no PS part); 84/12 **0.7** (many bugs); 85/2 **0.8** (usable); 85/4 **1.0** (first complete); 85/9 **1.5** (UI improved); 86/3 **2.0** (reliability, functions); 86/7 **2.5** (network strengthened); 86/12 planned **3.0** (unified UI). Size of 2.5 (PRINTED): **232,202 source lines, 1,380 classes, 18,601 predicates**. (Compare 4D-1: ~1,500 classes, ~18,000 predicates -- same period, rounded.)

**Fig.2-1 SIMPOS system structure** (PRINTED figure, semicircle, eyed at 300 dpi). Rings from centre: hardware; KL0 ring: **processor, memory, device, IPL, kana-kanji (カナ漢)**; supervisor ring: **situation (exception handling) (シチュエーション(例外処理)), process, pool, stream, whiteboard (ホワイトボード), utility (ユーティリティ), wildcard, directory, user management (ユーザ管理)**; I/O-media ring: **font management, window, text buffer, standard I/O buffer(s) (標準入出力バッファ), formatted I/O (書式付入出力), symbolizer (シンボライザ), library, file, printer, magnetic tape (磁気テープ), network**; programming-system ring (outer): **call counter, font editor, inspector/debugger, system debug tool (システムデバッグツール), window manipulator, document processing (文書処理), editor (PMACS/EDIPS), coordinator/shell (コーディネータ シェル), librarian, file manipulator, spooler manipulator, MT (magnetic tape) manipulator, file transfer, talk, terminal emulator (端末エミュレータ), mail, net-print manipulator**. Axis labels: programming system / I/O media system / supervisor / kernel = operating system; KL0 vs KL0/ESP.
  - Note: **coordinator and shell share one cell** (INFERENCE: in 2.5 the shell is the coordinator's command interface).

System composition (PROSE, p2-3, TRANSLATION): single user, multiple processes. OS = kernel (processor: multi-process; memory: allocation, address spaces, GC; device; kana-kanji conversion built into the **keyboard handler** so kanji can be input anywhere; IPL loads and initialises SIMPOS), supervisor (process, pool = containers for objects, stream = inter-process communication/synchronisation, wildcard, directory, user management = login users), I/O media system (window: mouse, multiwindow; font: management of fonts shown in windows; symbolizer: external (string) <-> internal (structure) conversion; file; magnetic tape; printer; network), programming system (PS: program-development tools and **manipulators** giving OS utilities by menu selection).

ESP section (p3-4, PROSE): standard input/output (`standard-input`, `standard-output`) as the OO example: char/line/structure I/O defined device-independently; device classes (file, window, printer) define per-character I/O and inherit the standard I/O class to get line/structure I/O. Drawbacks listed: dynamic method dispatch overhead (firmware support; use local predicates); a change to an inherited class forces recompiling subclasses (inheritance resolved at compile time); hard to know which class to use (manuals).

**User interface rules** (sec 4(2), PROSE, TRANSLATION):
  1. Every window doing character(-string) I/O is a **window with Pmacs function**, i.e. a standard I/O window in which Pmacs editing works during input.
  2. Menus are of two kinds, unifying the meaning of mouse input: (1) menus whose items are **operations**: fixed-length menus; (2) menus whose items are **objects of operations**: variable-length (scrollable) menus.

**Login processing** (sec 4(3), PROSE, TRANSLATION): per-user environment set at login by an **initialization file** etc.:
  1. **System menu items**: the system menu acts as SIMPOS's **command processor**, callable any time; starts, terminates, suspends, resumes processes. Two columns: **EXPERTS** (programs that may run as several instances in parallel) and **MEDIA SYSTEMS** (only one instance). Users add their programs to EXPERTS and delete unused ones.
  2. **Logical names for directories**; and a **default directory** used when none is given.
  3. **Initial program** run at login.
  4. **Automatic creation of PSs** (editors, debugger, ...) at login, with their windows displayed at specified positions.

**SCREENSHOT p4 "SYSTEM MENU"** (eyed, 300 dpi), title bar `SYSTEM MENU`:

  | col 1 (Experts) | col 2 (Experts, cont.) | col 3 |
  |---|---|---|
  | Experts (heading) | | MEDIA SYSTEMS (heading) |
  | Debugger | Escher | user process list |
  | Pmacs | Oekaki | window manipulator |
  | File | Queens | network |
  | Librarian | Squares | shell |
  | Font_editor | Bounce | whiteboard |
  | Edips | | kanakan initiate |
  | Spooler | | garbage collection |
  | | | login |
  | | | shut down |

  VARIANT vs TM-181 p3 listing (`printed/listings/TM-181_p03_system_menu.txt`, lower-case names, `file_manipulator`, spooler before font_editor, no col 2): here capitalised, **File** for the file manipulator, **Spooler** last, and a second Experts column of the user's **demo programs Escher, Oekaki, Queens, Squares, Bounce** -- i.e. the EXPERTS list is user-extensible as stated (these are hiroyuki's `demo.esp` classes, see below). Mouse cursor arrow next to `login`.

Program development cycle (sec 4(4), PROSE): edit source with the editor -> register class with the **librarian** and convert to executable code (compile) -> step/debug with the **debugger**; inspect slot values with the **inspector**.

**Editor (Pmacs)** (sec 4(5), PROSE): same features as 4D-2 (100+ commands; buffers accessible by name from any process; kana-kanji; customization in ESP).
**SCREENSHOT p5 Pmacs** (600 dpi, eyed): window label **`pmacs_1`**. The buffer holds the user's demo source (application code; grade SCREENSHOT). Per the copyright rule, only the system calls visible in it are listed:
  - `:get_mouse_position(W, X, Y)`;
  - `:draw_rectangle(W, X1, Y1, S, S, 1, filled, exclusive_or)`;
  - class `bounce` with `nature as_demo_program`, and `:goal(Obj)`, which calls:
    - `:create(#window, {size(manipulator), position(manipulator), title(" Hit any key to exit ...")}, W)` (the bracket may be `[`; it is unclear in print);
    - then `:erase_cursor(W)`, `:set_inside_units(W, 1, 1)`, `:activate(W)`, `:initiation_end(Obj)`, `:refresh(W)` and `:get_inside_size(W, Sx, Sy)`.
  (line ends hidden behind a popup are elided.) Mode line: **`PMACS(esp)[65,26] demo i3psi7::>sys>user>hiroyuki>demo.esp --74%--`** (node part read as "i3psi7::", partly blurred). Below it an empty echo line.
  Popup **`EDITOR MENU`**: **ABORT, List Buffers, Save All Files, Set Font, Set Echo Font, Set Window Size, From Whiteboard** (boxed = under mouse), **To Whiteboard**.
  Bottom **status line** (whole-screen, PROSE-INFERENCE): left `USER : hiroyuki` / `SIMPOS Version 2.50`; then inverse boxes `screen` and `EDITOR MENU` (INFERENCE: name of the window under the mouse / selected); right `08-Sep-86 Monday  14:03:42`. Background is a grey stipple ("screen").
  -> SCREENSHOT facts (application code seen on screen; 1986 v2.50): `#window` created with options `size(manipulator)`, `position(manipulator)` (INFERENCE: size/position chosen with the mouse by the window manipulator), `title(String)`; instance methods `:erase_cursor/1`, `:set_inside_units/3`, `:activate/1`, `:refresh/1`, `:get_inside_size/3`, `:get_mouse_position/3`, `:draw_rectangle/8` (args: W, X, Y, Width, Height, 1 (INFERENCE line width), filled, exclusive_or (ALU op)); program protocol `:goal/1` and `:initiation_end/1` on an `as_demo_program` object. Arity counts receiver.

**Librarian** (sec 4(6), PROSE, TRANSLATION): all classes are managed by the **library**; the **librarian** is the UI to it. Functions: (1) register/delete classes: from ESP source generate executable code, **interpreted code or directly executed (compiled) code**, selectable; delete registered classes; (2) change a class's executable code between interpreted and direct; (3) **save/load template files**: a template = per-class information (slot info, method and local-predicate code, inherited class names, referenced class names) saved to a file or loaded into main memory; (4) **batch commands**: a series of librarian commands invoked at once (useful to register many classes); (5) utilities: search information about OS and user classes.
**SCREENSHOT p5 Librarian** (600 dpi, eyed): window label **`librarian_1`**; left command menu: **Check, Catalogue, Compile** (highlighted), **Uncompile, Save, Load, Delete, Execute, Utility**; right transcript pane:
  [The screen transcription is kept locally, not in git, until the owner decides on quoting IPSJ papers at this length: pim/docs/nonlocal/lit/ipsj/LOCAL_transcriptions_36239_118681.md (gitignored). The facts drawn from it are listed below.]
  (spelling "Catalogging" as printed.) Popup **`CLASS NAME`** (variable-length operand menu): **DO IT, EXIT, ALL BUT SELCTED** (sic), **FROM WHITE BOARD**, then class names `test, demo_manager, bounce, squares, queens` (boxed, marked with an `x` = selected), `oekaki, escher, as_demo_program`. Status line `USER : hiroyuki`, `SIMPOS Version 2.50`, `screen`, `08-Sep-86 Monday 15:09:17`.
  - Facts: prompts `File Name>` and `Class Name>`; default shown in brackets `[test]`; cataloguing a file lists each class then `<class> end.`; a multi-select class menu with DO IT / EXIT / ALL BUT SELECTED / FROM WHITE BOARD (SCREENSHOT, v2.50). One source file may hold several classes here (demo.esp: 7 classes) -- VARIANT vs TR-057's "class source file holds exactly one class" (STRUCTURE s9).

**Debugger / interpreter** (sec 4(7), PROSE): runs ESP programs with symbolic trace over interpreted code, directly executed code and KL0 built-ins; **P&C model (Procedure and Clause Box Control Flow Model)** (Fig.4-1 PRINTED: procedure ports CALL, EXIT, FAIL, REDO; clause boxes Head/Body with ports unify, pick, exit, next, miss, redo -- same as TR-057 p8); spy points; multi-process debugging.
**Inspector** (sec 4(8)): shows/searches/changes object slot values and KL0 data; menu-based, mouse-driven; **called from the debugger and returns control to it**; can change a variable's value received from the debugger and return it, or bind an unbound debugger variable and continue.
**SCREENSHOT p6 debugger+inspector** (600 dpi, eyed):
  - Window **`Debugger_4`** with a right pane **`Variable`** (shows `B`). Trace lines (verbatim, wrapped):
    `(742)81 CALL builtin> add(532,7,A) ? step` / `(742)81 EXIT builtin> add(532,7,539)` / `(743)81 CALL builtin> divide(-22,2,A) ? step` / `(743)81 EXIT builtin> divide(-22,2,-11)` / `(744)81 CALL builtin> add(218,-11,A) ? step` / `(744)81 EXIT builtin> add(218,-11,207)` / `(745)81 CALL> do($window,539,207,546,417,7,-22) ? step` / `(745)81 unify> do(A,B,C,D,E,F,G) :- less_than(B,0)->subtract(...),minus(F,I),'$atom$B008'(...) ...` / `(745)81 pick> do($window... ) :- less_than(...` ... ending with a `?` prompt.
    -> Format: `(<invocation no.>)<depth> <PORT>[ builtin]> <goal> ? <command>`; ports seen: **CALL, EXIT, unify, pick**; command typed **`step`**; builtins `add/3`, `divide/3`, `subtract/3`, `minus/2`, `less_than/2`, `not_less_than/2` (KL0 built-in names, SCREENSHOT). Objects printed as **`$window`**; compiler-generated predicate `'$atom$B008'` (INFERENCE: if-then-else expansion).
  - Window **`Inspector`**, subtitle **`$window@1:4087FC`** (object print form `$<class>@<n>:<hex address>`); slot list (name, then value): **`dependency` = `none`; `echo_buffer` = `$list@1:40089F`; `employers` = `$extensive_list@1:40089C`; `error_report_window` = `nil`; `error_status` = `normal`; `exposed_flag` = ...** (cut off). Right pane **`Memory`**: `Variables`, `Predicate`, `$window@1:4087FC` (history). **`Command`** pane: **exit, parameters, break, from_WB**.
    -> SCREENSHOT facts: in v2.50 a `window` instance has slots `dependency`, `echo_buffer` (a `list`), `employers` (an `extensive_list`), `error_report_window`, `error_status`, `exposed_flag` (alphabetical listing; more below the cut).
  - A window titled **`Hit any key to exit`** shows the bounce demo (squares bouncing). Status line `USER : hiroyuki / SIMPOS Version 2.50 / screen ... spool / 08-Sep-86 Monday 15:19:37` (`spool` box at right: INFERENCE spooler status indicator).

**Font editor** (sec 4(9)): create/modify fonts of various shapes, sizes, character sets; change system fonts, add character fonts, create new fonts; **icons are made with the font editor too**; all mouse. SCREENSHOT p6: icon editing (faces) with a row of small face icons at top; same right panel as 4D-3 (black/white/inverse, dot/line/square; Char mode, Help; Draw, Draw Line, Clear, Move, Set Sample, Real Size, Circle, Scale, Add, Swap, Reflect, Box, Cut) with **Width 90, Height 70, Bias 0**; sample icons below. INFERENCE: icons are glyphs of an icon font.
**Japanese input** (sec 4(10)): JIS 16-bit codes for all characters; kana-kanji in the keyboard (software); Pmacs word-processor style input.
**SCREENSHOT p6 kana-kanji in Pmacs** (600 dpi, eyed): window **`pmacs_4`**, Japanese text being converted; popup titled **`KANAKAN`** with numbered candidates `0. 洗濯する  1. 選択する  2. せんたくする`; mode line **`PMACS(esp)[30,18] *-3*  --Top--`** (buffer `*-3*`); echo line **`M-\`** (INFERENCE: the conversion command key); bottom system line shows the reading `せんたくする` and candidates `0. 洗濯する 1. 選択する 2. せんたくする`, and the key help **`>MENU(PF16) PF10=ON_OFF, PF0-PF6=MANAGE_KEY, PF7=CANCEL.`** (the "PF0" digit is blurred; could be PF8/PF9). -> keycodes PF0..PF16 exist on the PSI keyboard (SCREENSHOT).
**Document processing** (PROSE, p7): Pmacs-entered Japanese flowed into a layout.

**Manipulators** (sec 4(11), PROSE, TRANSLATION): utilities by menu selection:
  1. **window manipulator**: change window attributes such as position and size;
  2. **file manipulator**: list file names, copy/delete, **pattern search, word count**; access files on other PSIs and general-purpose machines over the network;
  3. **spooler manipulator**: show spooled print jobs, cancel, reorder;
  4. **magnetic tape manipulator**: initialise tapes, save/restore disk files to tape.
**SCREENSHOT p7 manipulators** (600 dpi, eyed): 
  - **`spooler manipulator`** window: pane `Command`: **Direct, Spool, Test, Manipulate**(? highlighted, blurred), **Cancel, EXIT**; pane `Listing`: `0 : i3psi7::monoe;85.dat.1`, `1 : i3psi7::josen;13re..1`, `2 : i3psi7::jiho_saiten.dat.1` (file names blurred). -> pathnames carry a node prefix `i3psi7::` and a version suffix `.1`.
  - **`file_manipulator_?`** window, header shows a directory (`>sys>user>???`, blurred), list `INSTLCGS.COM.1, INSTLCMN.COM.1, INSTLOTH.COM.1, SOURCE.DAT.1, ... login.c?d.2, m_newsmo.dat.1, m_init.dat.1` (file name . extension . version). Popup titled with the file name (`jiho_saiten.dat.1`?) with items: **delete, rename, copy, copy to fdd, append, describe, type, dump, word count, pattern search, to whiteboard**.
  - **`mt_utility_window/3`** with menu **`tape menu`**(title blurred): **initialize volume, show volume label, show file label, save to MT, restore from MT, attribute, exit**.
  - Status line right shows two inverse boxes (`screen`? and a window name, blurred) and `08-Sep-86 Monday 15:54:04`.
**Network** (sec 5): LAN (Ethernet-like, coax, LIA "Line Interface Adapter" here), bridge, gateways to NTT DDX; **NCP** controls the LIA. (1) **Talk**: initial message to the other user; on acceptance each PSI gets an **input window and an output window**; full duplex. SCREENSHOT p7 (two screens): window headers **`TALK INPUT` / `TO i3psi7 :: reiko`**, **`TALK OUTPUT` / `FROM i3psi7 :: reiko`**; on the other screen `FROM i3psi009 :: hiroyuki` (node digits blurred); bottom of input window: **`BYE  MODE`** buttons; status line `USER : reiko`, and an inverse box `talk_input_window/?`. -> address form `<node> :: <user>`.
  (2) **E-mail**: mailboxes centralised on one PSI; Pmacs used to edit outgoing mail; multiple recipients; list/show/print/save/delete received mail; **new-mail notice at login and interrupting during use**; (5) **electronic bulletin board** = shared mailbox. (3) **Remote file system**: create/delete, open/close, read/write, status query of remote files; transfer both ways; a PSI with a large disk can be a file server. (4) **Remote print**: laser-printer PSI as print server.
References (p8): Hattori et al. "SIMPOS operating system" IPSJ 29th conv. pp285-304, Sep 1984; Kurokawa et al. "SIMPOS programming system" IPSJ 30th conv. pp295-316, Mar 1985; Ishibashi et al. "SIMPOS -- user interface and development process" IPSJ Computer System Symposium pp107-113, Dec 1985; Ishibashi et al. "Programming environment in SIMPOS", 1985 joint conv. of EE-related societies pp5.69-5.72, Sep 1985; Chikayama et al. 4D-1..4D-12 (IPSJ 33rd). ALL NOT HELD (leads).

### 3J-8 (118681) "Customization function of the SIMPOS librarian" (SIMPOSライブラリアンのカスタマイズ機能)  **KEY SOURCE**
**Kodama Yasuko** (児玉泰子), Fujimoto Seiji, Mitsubishi Electric Computer Systems (Tokyo). IPSJ 40th conv. (spring 1990) pp.933-934. Eyed p1-p2, figures zoomed 300 dpi.
- **Author link**: cil's `class library_utility` is stamped `mkpsi000::>sys>user>yasuko>UT.esp.2, 29-Jul-88` (README s2). INFERENCE (strong): "yasuko" = Kodama Yasuko, Mitsubishi, the librarian's developer -> cil's `library_utility` is very probably a copy of real Librarian code (see POSSIBLE SIMPOS CODE).
- Librarian = a SIMPOS programming system giving operations on ESP **classes and packages** via windows and menus (PROSE). The subsystem **library** manages classes and **packages** (sets of classes); **all classes running on SIMPOS are registered in the library**. The librarian provides as commands: register/delete/search classes and packages, view inheritance/reference relations, manage executable code; offered as a **command menu** using the window system (sec 2).
- Operation: pick a command from the menu by mouse click, then type the needed parameter (e.g. source file name for class registration) **into the text window**; almost all commands are in menus (sec 2).
- **Customization introduced in SIMPOS 5.0** (sec 1). Three functions (sec 3): (1) add/change commands by programs using the librarian's **part classes** (部品クラス); (2) rearrange the command menu including its hierarchy; (3) replace the librarian's whole I/O part (windows and menus) with user-defined ones.
- **Fig.1 "standard librarian initial screen (part)"** (SCREENSHOT, eyed 300 dpi, v5.x 1990): window title **`librarian 49 ( default: user )`** (digit 49 or 48, blurred; Fig.3 shows `librarian 48 (default: user)`) -- INFERENCE: `librarian <process no.> (default: <default package>)`; left command column: **Set up, Check, Catalogue, Save, Load, Delete, Package, Execute, Utility, ESP tool, [Close]**; empty text pane at right. Submenus (separate windows with title bars):
  - **`set_up_menu`**: **Set up, Save state, Check menu item**
  - **`package`**: **Set default package, Define package, Define environment, ----, Delete package, Delete environment, ----, Retrieve, ----, Other command, ----, [Exit]**
  - Delete, Utility, ESP tool have submenus too (shown as dashed leaders, not expanded).
- **Fig.2 "standard librarian menu definition"** (PRINTED, transcribed in full as printed, ellipsis is in the original):
  [The Fig. 2 transcription is kept locally, not in git, until the owner decides on quoting IPSJ papers at this length: pim/docs/nonlocal/lit/ipsj/LOCAL_transcriptions_36239_118681.md (gitignored). The facts drawn from it are listed below.]
  Menu definition = list of (menu item string, command name) pairs; nesting = top/sub-menu hierarchy; **`up`** returns to the parent menu. Stored in the **librarian initialization file** (ライブラリアンの初期化ファイル); edit it with the editor and save it to get a new menu next time (sec 4).
  -> librarian command names (PRINTED, v5.0): `set_up_menu`, `set_up`, `save_state`, `check_menu_item`, `check`, `catalogue`, `save`, `load`, `delete_menu`, `delete`, `abolish`, `forget`, `delete_resource`, `up`.
- Adding a command (sec 4, PROSE): define a class inheriting the system's librarian functions, plus a class defining the new command; their combination is a librarian with both.
- **Fig.3** (SCREENSHOT): the same menus re-labelled in Japanese: top: 初期設定 (Set up), パッケージの設定 (Set package), クラスの登録 (register class), クラスのロード (load class), クラスの削除 (delete class), パッケージ メニュー (package menu), ユーティリティ メニュー (utility menu), アイコン (icon); `set_up_menu`: 初期設定, 状態セーブ (save state), メニュー項目チェック (check menu item); `package`: パッケージの登録 (register package), パッケージ環境の登録 (register package environment), ----, パッケージファイルの作成 (make package file), パッケージ環境ファイルの作成 (make package-environment file), ----, 拡張機能 (extended functions). TRANSLATIONs mine. (Shows menu items can call commands under new labels and new groupings, e.g. "make package file" = INFERENCE `save_package`.)
- **Fig.4 internal structure** (PRINTED figure): the librarian = **command execution part** (コマンド実行部) -> uses -> **program interface part** (プログラム・インタフェース部, does the real work, talks to the **library system**) and **I/O part** (入出力部, talks to the **window system**). Swapping the I/O part changes windows/menus completely; using only the program interface part lets other subsystems simulate librarian functions (sec 4).
  - INFERENCE: matches cil's `library_utility` natures (`librarian_version`, `librarian_class_generator`, `librarian_delete`, `librarian_package`, `librarian_spy`, `librarian_reference`, `librarian_fdd`, `librarian_subroutine`): these look like the "part classes" / program-interface part.
- Future (sec 5): **SIMPOS 6.0 in development**; selecting the menu initialization file from several files.
- References: Chikayama, "ESP Reference Manual", ICOT TR-044, 1984; **"Small PSI/SIMPOS operating manual, basic volume (SIMPOS 5.0)" (小型化PSI/SIMPOS操作説明書, 基本編), ICOT 1988** -- NOT HELD (lead: this is the user manual).

### 7G-2 (118591) "SIMPOS volume compaction" (ボリューム・コンパクション)
Kato Tatsuo, Sato Tadashi, Mitsubishi Electric Computer Systems (Tokyo). IPSJ 40th conv. (spring 1990) pp.759-760. Eyed p1 (text at 300 dpi), p2 figures at 150 dpi. File system; outside UI scope; key facts only (PROSE, TRANSLATION):
- SIMPOS file system: tree-structured, **Unix-like**, data-scattering type. Disk unit = **data block, 4 KB**. Volume initialisation creates the **system core**: volume label; minimal **file file** (ファイル・ファイル, manages all files); **free block map file**; **free i_no map file** (フリーi_noマップ・ファイル); minimal root directory file.
- **File file** = record-form file; creating a file allocates one record; first half of the first record = file attributes, second half = block numbers owned by the file; overflow -> **map records** in the file file. The file file's own map is fixed in the system core.
- **Directory** = a file of **directory records** (entry name and attributes), each pointing to a file-file record by **record number**. Fig.1 example: `>sys` holds `user 256`; `>sys>user` holds `me 342`; `>sys>user>me` holds `file 788`, whose record has a `map__record`; path written `>sys>user>me>file`.
- SIMPOS **4** reduced scattering at run time (freed blocks/records registered in bit-map files; allocation near the file's existing resources); SIMPOS **5** adds volume compaction: **directory segments** (all of a directory's records, file-file records and blocks) moved to contiguous block numbers as **compaction segments**, placed in directory-tree order (Fig.3: `system core`, `>sys segment`, `>sys>user segment`, `>sys>user>me segment`, `>sys>user>me>you segment`, `>sys>library segment`); free space reserved inside each segment. Tree in Fig.3: `>` -> `sys` -> {`user` -> {`me`, `you`}, `library`}.
- The SIMPOS **disk handler** guarantees contiguous block numbers lie on the same/adjacent cylinders.

### 4E-7 (115246) "PSI-SIMPOS network: TELNET" (1988, IPSJ 37th conv., pp.502-503; Amanuma, Azuma, Hoshi, Tsuchikawa). Eyed p1-p2 (300 dpi).
- User programs reach TCP/IP through the **`tcpip_socket`** object; they call tcpip_socket predicates (PROSE, TRANSLATION). Layers below it: CIOP handler process, then the board (C-bus I/O controller, XVLAN).
- TELNET has four parts (PROSE, TRANSLATION):
  - (1) the TELNET process;
  - (2) a receiver process;
  - (3) window objects: several command-input windows plus one terminal-emulation window, managed together by a **"window folder"** (ウィンドウ・フォルダ) object; **clicking the window with the mouse shows a command menu**;
  - (4) the NVT (Network_Virtual_Terminal), a single object that inherits several classes.
- Negotiated options are "echo" and "suppress-go-ahead" (PROSE).
- Fig.2 boxes (PRINTED figure): menu, emulate window, window folder, log file, tcpip library.
- Escape sequences are supported, and several TELNET sessions can run at once (PROSE).
- INFERENCE: the held partition class `telnet_terminal` is probably the emulation window.

### 4E-8 (115247) "PSI-SIMPOS network: remote object access (ROAM)" (1988, 37th conv.; Mori, Yoshida K., Fukui, Ishihara). Eyed p1-p2.
- Remote object mechanism (PROSE):
  - the requester holds a temporary **proxy object** and a requester process;
  - at the far end, a **receptionist process** creates a proxy (agent) process that acts on the real object.
- Logging uses **before/after demons** and is about 500 lines of ESP (PROSE).
- Printed log example (PRINTED, short fragment): `** remote_access_log **`, `user_name : icpsi909!superuser`, `open_time : 88-05-26 11:28:15`, `file_name : icpsi900::>sys>user>mori>database32>atoms.db.1`, `command : a`.
- This gives three formats (PRINTED):
  - user = `node!user`, and a **superuser** account exists;
  - a full remote pathname = `node::>dir>...>name.ext.version`;
  - dates are `YY-MM-DD hh:mm:ss`.

### 4E-9 (115248) "PSI-SIMPOS network: FTP" (1988, 37th conv.; Kajiyama, Yoshizumi, Osaki). Eyed p1-p2.
- Transfer modes (PROSE):
  - image and ASCII, with ASCII <-> JIS 16-bit conversion;
  - remote delete and rename;
  - change directory and list, on both the local and the remote side.
- Processes (PROSE): user side UPI/UDTP, server side SPI/SDTP.
- Two input modes (PROSE, TRANSLATION):
  - **"command interpreter mode"**, prompt `FTP>` (PRINTED in figure);
  - **"menu mode"**.
- Windows (Fig.2 SCREENSHOT/diagram):
  - main window titled `FTP`, with a file-select menu and a command menu;
  - interpreter window (`FTP>`);
  - host-name setting window;
  - directory-operation window and menu (cd, list, wildcard transfer);
  - file-operation window, titled with the file name, with its own menu.
- The FTP function is also offered to programs as objects with methods (PROSE).

### SIG-OS 23-1 (26580) "Operating system of PSI" (PSIのオペレーティング・システム) 1984-06-08. Hattori T., Kurokawa, Sakai, Tsuji, Chikayama, Takagi, Yokoi. Handwritten manuscript, 10 pp.
Eyed p1, 4, 5, 7, 8, 9. Other pages OCR only.
- This is a third witness of the TM-061/TM-065 content (1984, SIMPOS pre-1.0). It uses the underscore spelling.
- p7 `bare_window` is identical to TM-065 (PRINTED).
- p8 `with_border` matches the **TM-061 variant**: `Window!border_flag == off, !`, and its second demon has no cut (PRINTED; VARIANT vs TM-065, see PIM/docs/simpos/printed/VARIANTS_tm0061_vs_tm0065.txt).
- `with_label` and `window_with_border_and_label` are identical to the TR/TM text (PRINTED).
- p5 Fig 3.1, the layer diagram, is the same as TM-061 (PRINTED figure). From top to bottom:
  - coordinator, editor, transducer, interpreter/debugger, librarian;
  - windows, network, file;
  - process, pool, stream, world;
  - processor, memory, device.
- p5-7: the class `file` listing, as in the TR/TM (PRINTED).
- p4 lists the kernel classes **process, stream, pool, world, processor, area, disk, keyboard** (PROSE).
- p9 history (PROSE, TRANSLATION):
  - design began autumn 1982; a software group formed June 1983;
  - the class specification was complete at the end of FY1983;
  - an ESP cross compiler, linker and simulator were built;
  - PSI was released to the group in March 1984;
  - a **provisional SIMPOS was released internally at the end of Sept 1984**;
  - **v1 was planned for the end of FY1984** (March 1985).

### SIG-ARC (24478) "PSI/UX architecture" 1991-11-21 (Masuda, Matsumoto, Ikeda). Eyed p2-5.
- SIMPOS window system on PSI/UX (PROSE + figure, TRANSLATION):
  - the whole SIMPOS screen is shown inside **one X window**;
  - window control, mouse and keyboard are still processed by SIMPOS itself.
- Its parts (PROSE):
  - the **SIMPOS window manager** (parses requests, generates drawing commands, distributes mouse/keyboard input);
  - a window communication handler;
  - the **SIMPOS window server**, an X client at the Xlib level with a "SIMPOS Widget" on the X Intrinsics; it can display on other X terminals.
- Fig.2 (PRINTED figure): only the kernel I/O handler (A) and part of the I/O subsystem (B) were rewritten to go through UNIX. The rest is **object-code compatible** with PSI-II.
- Communication logical channel: 128 KB of VME shared memory (PROSE).
- The SIMPOS file area is separate from UNIX, because file-name length, version management and protection differ; the disk cache sits in SIMPOS memory (PROSE).
- Sockets: one UNIX socket-server process per SIMPOS socket; RPC is available on SIMPOS (PROSE).
- CPU: 1.4 MLIPS; 5-stage pipeline D/A/R/S/E; EXTKERNEL is mentioned (PROSE).

### Mitsubishi Denki Giho Vol.60 No.9 (Sep 1986) special issue "AI workstation MELCOM PSI" (lit/journals/mitsubishi_giho/8609.pdf)
**(a) "AI workstation MELCOM PSI"** pp.597-602 (PDF p11-16). Authors from the footer, uncertain OCR: ?Hattori, Masuda, Kawakami, Ikeda, Nakajima.
Eyed p15, p16; Fig.8 zoomed at 300 dpi.

- Software structure, Fig.7 (PRINTED figure, TRANSLATION):
  - operating system = kernel supervisor (カーネルスーパバイザ) + I/O media system (入出力メディアシステム = window system + file system);
  - programming system = editor, librarian (ライブラリアン), debugger;
  - basic application system = font editor, document processing system.
- Text (PROSE, TRANSLATION):
  - users may freely inherit and combine the window classes to define their own windows;
  - the file system supports binary files without record structure, and fixed-length-record "table files";
  - directories are a tree, and a file is named by path name.
- Editor (PROSE): EMACS-like multi-window screen editor:
  - many commands working on character, word, line and page;
  - comment handling, case conversion, narrowing, **auto-save mode**;
  - built-in kana-kanji conversion with candidate selection by **menu** and batch conversion.
- Librarian (PROSE): manages class sources and objects:
  - class registration and compilation;
  - analysis of inheritance and reference relations between classes;
  - search of the classes in the system by name prefix, and search by predicate name.
- Debugger (PROSE): an extension of the Prolog **Box Control Flow model**:
  - step execution per predicate;
  - trace;
  - detailed display of argument information;
  - display of object contents.
- **Fig.8 "running the programming system"** (SCREENSHOT, dated **12-Apr-86 Saturday 11:30:23**, status line `USER : demo`, a `spool` indicator and a `debugger_1` label). Five windows:
  - **`debugger_1`** window, with a `Variable` pane on the right:
    - trace lines (exact): `?- :initialize(#eight_puzzle).` / `(1)0 CALL new> location_element(loc@1:25C066,A),method_call(A,initialize) ? step` / `(2)1 CALL builtin> location_element(loc@1:25C066,A) ? step` / `(2)1 EXIT builtin> location_element(loc@1:25C066,#eight_puzzle) ? step` / `(3)1 CALL> :initialize(#eight_puzzle) ? step` / `(3)1 EXIT> :initialize(#eight_puzzle) ?`.
    - Trace format: `(seq)depth PORT [kind>] goal ? reply`; kinds `new>`, `builtin>`, none for methods; a location appears as `loc@1:25C066`.
  - **Debugger pop-up menu** (exact): `Method / Step / Skip / Leap / Fail / Retry / No trace`, then a separate box `PREDICATE` (highlighted) / `clause`.
  - **`librarian_1`** menu (exact): `Check / Catalogue / Compile / Uncompile / Save / Load / Delete / Execute` (the box continues below and is hidden; compare 36239's Sept-86 menu, which ends `... Execute / Utility`).
  - The librarian output pane (exact): `Catalogging "8PZL.ESP"...` / `eight_puzzle` / `eight_puzzle end.` / `eight_puzzle_window auto loaded.` / `eight_puzzle_window end.` / `eight_puzzle_message auto loaded.` / `eight_puzzle_message end.` / `eight_puzzle_board auto loade[d]`. NOTE the spelling **"Catalogging"** (sic).
  - **`pmacs_1`** window showing ESP source:
    - `:get_board(Class,Class!board) ;`, `:get_message_window(Class,Class!message_window) !`, `:get_window(Class,Class!window) ;`
    - `:initialize(Class) :- ! , :create(Class,Program), :create(#process,Process), :set_sub_priority(Process,2), :activate(Process,Program) ;` then `instance`.
    - Mode line `PMACS(esp)[48,17] *-1* 8PZL.ESP.7 --1%--`; minibuffer line `Read: >sys>user>demo>8PZL.ESP.7`.
  - A directory listing window: `8pzl_list.com.4`, `BPARSE.ESP.1`, `BUPDAT.ESP.1`, `BUPINP.ESP.1`, `BUPVPT.ESP.1`, `CHWIND.ESP.1`, `DGDATA.ESP.1`, `DGFDD.ESP.1`, `DGFXD.ESP.1` (top partly hidden).
- What the screenshot gives (SCREENSHOT unless marked):
  - **process class**: `:create(#process,P)`, `:set_sub_priority(P,2)` and `:activate(P,Program)`, i.e. create/2 cmethod, set_sub_priority/2 and activate/2 imethods (arity counts receiver);
  - the user directory `>sys>user>demo`, so user `demo` has home `>sys>user>demo`; file versions `.N`; a `.com` command file `8pzl_list.com.4`;
  - the bottom status line: `USER : <name>` on the left, the selected window's title, `spool`, and `DD-Mon-YY Weekday hh:mm:ss`.
- Version: April 1986, so SIMPOS 2.0 (released spring 1986 per 4D-1) (INFERENCE).

**(b) "Object-oriented logic programming language Extended Self-contained Prolog"** (ESP) pp.~603-606 (PDF p17-20). Kawakami, Yoshida, Ueda, Kondo. Eyed p19, p20; Fig.8 code zoomed at 300 dpi.
- p19, class `standard_io_window` (PROSE list, TRANSLATION):
  - a **3-argument class method `:create`** creates an instance (window);
  - instance methods:
    - `:activate` displays the window on screen;
    - `:select` makes it the input window;
    - `:putl` writes a string;
    - `:gett` reads input;
    - `:set_position` moves the window;
    - `:putc` writes a character.
- **Fig.8 (PRINTED, application code)**, class `moving_window`:
  (Per the copyright rule, the code is not transcribed in full.) Its structure:
  - `class moving_window has nature standard_io_window ;`;
  - a class-part `:create(CLASS, Window)` that calls `:create(CLASS, [size(400,200), position(0,0), title("moving window")], Window)` and then `:activate(Window)`;
  - an instance method `:move(Window)` that calls `:select(Window)`, `:putl(Window, "Input X")`, `:gett(Window, X)`, the same for Y, and then `:set_position(Window, X, Y)`;
  - a local `prompt(Window) :- :putc(Window, #">")`.
  - Grades: standard_io_window create/3 (cmethod; options list `size(W,H)`, `position(X,Y)`, `title(String)`), activate/1, select/1, putl/2, gett/2, set_position/3, putc/2. PRINTED (usage in printed code) + PROSE.
  - NOTE: `:set_position(Window,X,Y)` = set_position/3; `:putc(Window,#">")` takes a character constant `#">"`.
- Fig.9/10 (SCREENSHOT, **17-Apr-86 Thursday 19:47:05**, `USER : me`, `spool`):
  - the `moving window` window is at the top left;
  - the `debugger_1` window (with a `Variable` pane listing `Window`) shows `?- :create(#moving_window,Window).` / ` Window= $moving_window` / `?- :move(Window).`;
  - the moved window shows `Input X>100.` / `Input Y>600.`.
  - So the debugger top level is `?-`, bindings print as `Var= value`, an instance prints as `$classname`, and a class object is `#classname`.
  - Input is terminated with `.` (SCREENSHOT).

**(c)** The 8609 issue also has EXT (expert shell) articles. They say the EXT rule editor uses the **Pmacs editor function** provided by SIMPOS (PROSE), and EXT uses multi-window, pop-up menus and the mouse. Application only; not further extracted.

### Mitsubishi Denki Giho Vol.62 No.10 (1988) pp.879-884, Hiratsuka, Akita: "Software development support environment for knowledge processing" (知識処理のソフトウェア開発支援環境) (journals/giho_8810_8810.pdf, PDF p43-48; text read in the text layer; p46-47 eyed at 100 dpi). Eyeing showed that Fig.7 (p46, folio 882) is a flow figure: editor -> class source; library/librarian internally calls the ESP compiler -> class template; object composer (refers to the program base) -> class object; debugger/inspector run it. Table 1 maps ESP terms to conventional ones (class template = object module; class object = load module; object composer = linkage editor). Fig.8 (p47, folio 883) is a schematic, NOT a screen image: a bitmap display with a system menu, librarian, editor, debugger and inspector windows; "multiwindow"; a mouse. Its text: the system menu starts processes; window selection; command-menu selection. Grade PRINTED (figure).
- Librarian pipeline (PROSE, TRANSLATION):
  - the librarian calls the compiler: class source -> **class template** ("object module");
  - it then calls the **object composer** (オブジェクトコンポーザ, linkage editor), which consults the **program base** (プログラムベース) to resolve inheritance: template -> **class object** ("load module");
  - the library registers sources and templates in the program base;
  - also: incremental compilation, dynamic class invocation, symbol management.
- Pmacs has several text buffers shared between processes, e.g. editor <-> debugger (PROSE).
- A **whiteboard** (ホワイトボード) passes data between windows (PROSE). Compare the 36239 inspector command `from_WB`.
- Debugger (PROSE):
  - per-predicate trace, break/resume, backtrack/retry, showing and changing variables.
- Inspector (PROSE): classes, symbols, and heap/stack/string structures.
- PSI-II: up to 160 MB, 400 KLIPS (PROSE).

### Mitsubishi Denki Giho Vol.63 No.7 (1989) pp.549-553, Ikeda, Yanada(?), Yoshinaga: "AI workstation MELCOM PSI II" (8907.pdf p34-35, eyed at 200/100 dpi)
- "SIMPOS II" is Mitsubishi's name for SIMPOS on PSI-II (PROSE).
- **"Currently version B00 (B00版) has been released"** (PROSE, p34). This is Mitsubishi product numbering; the mapping to ICOT 4.x/5.x is unknown.
- All program modules (classes) are managed uniformly by the **library** (ライブラリ): inheritance relations and dynamic class invocation (PROSE).
- The **debugger inherits the Pmacs screen editor**, so trace output in the debugger window can be edited and saved (PROSE).
- Fig.4 "SIMPOS II layer structure" (PRINTED figure, rings from inside out):
  - hardware;
  - memory management, device management, tracer, IPL;
  - process management, user management, pool;
  - window, network (TCP/IP, MNA-P), file;
  - editor (PMACS), debugger + inspector, librarian;
  - Acekit, EXTKERNEL II;
  - user program.
  - Labels underneath: I/O management, supervisor, kernel = OS; PS = programming system; AP = construction tools.
- **Color window system** (new in this version, PROSE + Fig.5, TRANSLATION):
  - each window may set its own display colours;
  - parent, child and grandchild windows can share colours;
  - colour windows are program-compatible with monochrome windows.
- How colour works (PROSE + Fig.5):
  - a colour window has a **colour palette** (カラーパレット) table holding several **colour pairs** (カラーペア) of two colours (1st/2nd colour, RGB each), mutually inverse;
  - a window with only one colour pair is defined to be a monochrome window;
  - programs specify colours by **colour number** on the palette (Fig.5: numbers 0/1 = pair 0, 2/3 = pair 1);
  - sharing a palette shares colours between parent and child.
- Network (PROSE):
  - TCP/IP with FTP and TELNET applications; with TELNET, one SIMPOS window acts as a terminal of another computer;
  - MNA-P peer file transfer.
  - The user creates an instance of a network class and sends it messages; the predicates named are **`connect`, `send`, `receive`** (PROSE). INFERENCE: the `tcpip_socket` methods.

### Mitsubishi Denki Giho Vol.65 No.6 (1991) pp.596-601, Yuasa, Ueda, Matsumoto: "MELCOM PSI/UX series overview" (9106.pdf PDF p80-87; Table 2 on PDF p86 (folio 80(600)) eyed at 100 dpi and it matches the transcription below; Fig.5-8 not eyed). Vol.65 No.6 confirmed from the page footer
- Table 2, **"SIMPOS development/execution environment"** (PROSE, TRANSLATION):
  - debugger/interpreter;
  - **librarian**: central management of programs and objects, registration, checking and display of management info;
  - **inspector**: takes out and changes objects during execution;
  - **PMACS**: "screen editor beyond EMACS";
  - **font editor**;
  - Japanese input;
  - **multi-terminal support** (M3300 workstations attached to PSI/UX): file transfer, file/library commands, editor and "ESP debugger subset";
  - **TRANSPRO-E/P** conversion between DEC-10 Prolog and ESP;
  - **tracer** (KL0 machine-instruction level);
  - memory management: automatic GC, and **"GC can also be forced from the system menu"**;
  - process management;
  - **user management**: user registration and environment setup at login;
  - **pool**: methods for array, list, stack, bag, set ...;
  - **window**: overlapping multiwindow; the **window manipulator** (ウインドウマニピュレータ) changes a window's state, position and size by mouse;
  - network: TCP/IP, FTP, SMTP, NFS;
  - file: hierarchical like UNIX; the **file manipulator** (ファイルマニピュレータ) searches, outputs and manages files by mouse;
  - EXTKERNEL II, Acekit.
- Fig.6 (from the text layer only): a SIMPOS volume is one UNIX partition. Paths `>SYS>...>me>` (SIMPOS) vs `/me/guest/src/` (UNIX) are shown side by side.
- Fig.7: SIMPOS window manager -> communication handler -> SIMPOS window server (an X client, Widget/Intrinsics/Xlib); other hosts' X servers can show the SIMPOS screen. This matches 24478.
- RPC over XDR on SIMPOS, so SIMPOS can run servers and clients (PROSE).

### Fujitsu Sci. Tech. J. 26(1), Apr 1990, J. Tanaka et al., "Overview of an Experimental Reflective Programming System: ExReps" (fstj V26_N01 PDF p92-101; p99 eyed, status bar zoomed at 400 dpi)
- ExReps is a GHC system that runs on PSI-II under SIMPOS. Its screenshots show real SIMPOS screen chrome.
- **Status line of Fig.9** (SCREENSHOT, exact), on two rows:
  - left: `USER : demo` / `SIMPOS Version 4.2`;
  - middle: `screen` / `editor_buffer_window/19`;
  - right: inverse boxes **`SWAPPED`** and `spool`;
  - date: `12-Sep-89 Tuesday 10:25:41`.
- What this establishes:
  - **SIMPOS 4.2 was in use in Sep 1989** (SCREENSHOT).
  - The status line keeps the 1986 layout.
  - A `SWAPPED` indicator exists (INFERENCE: a swap/paging state).
  - A window is named in the class/number form `editor_buffer_window/19`. The middle field shows `screen` over the window name; INFERENCE: the object under the mouse and the selected window.
- The application windows (ExReps's own: command panes `exec abort / resume halt / state scroll`, `enter halt scroll`) are application UI and are not extracted. Other pages (p97, 98, 100) show `editor_buffer_window/11` in the same kind of status line (text layer).

### Mitsubishi Denki Giho Vol.61 No.7 (1987) PDF p28 (folio 22(532)), machine-translation application on PSI (eyed at 100 dpi). Fig.12 names the Pmacs classes only by description: a class for file operations, a class for case conversion, a class for kana-kanji conversion (no class identifiers printed). Fig.11 shows the application's popup `REMOVE ABORT`. Application only.
- The translation system inherits the **Pmacs classes** to get almost all Pmacs editing functions in its own window (PROSE, TRANSLATION).
- Application only.

### Computer Software (JSSST) Vol.8 No.1 (Jan 1991) pp.54-70: Imanaka T., Fujimoto N., Uehara K., Toyoda J., "WINCS: a development support system for window-control programs in ESP" (ESP言語上のウィンドウ制御プログラム開発支援システム) (journals/jstage-wincs_wincs_8_1_54.pdf, 17 pp, no text layer) **KEY SOURCE for window classes**
Eyed PDF p2, 3, 5, 7, 8, 12; the rest is tesseract jpn OCR only. Received 1989-07-10. The work was done on MELCOM PSI II under SIMPOS, so the facts are about SIMPOS ~4.x (1989).

- **Approach** (PROSE, TRANSLATION): a window-control class is built by multiply inheriting SIMPOS **window classes** (ウィンドウクラス). WINCS picks and orders them from attributes the user chooses in menus, using a TMS.
- **"SIMPOS provides about 40 window classes"** (約40種類) (PROSE, p3/folio 56).
- **Example class** (PRINTED, p2/folio 55):
  - `class my_window has nature as_output, as_graphics, inferior_window`;
  - meaning, TRANSLATION: "makes an output window", "can output graphics", "implemented as a hierarchical window".
- **Example message** (PRINTED, p3): `:draw_circle(#my_window, X1, Y1, R, 1, solid, set)` draws a circle. That is draw_circle/7: object, centre X, Y, radius, line width, line style `solid`, ALU op `set`. NOTE: the printed receiver is the class object `#my_window`.
- **Inheritance constraints printed as facts** (PROSE, p3; from the SIMPOS manual, cited as ref [12]):
  - `with_label` must be inherited BEFORE `inferior_window` (an order constraint);
  - `as_menu` cannot be used together with `as_graphics` (a conflict);
  - `as_menu` requires `as_mouse_input`; `as_mouse_input` does not require `as_menu`;
  - one of the **base classes** `inferior_window`, `popup_window`, `temporary_window` is mandatory (p7-8);
  - `as_output` and `as_menu` conflict in one window, unless the window is split with **`as_superior`** ("provides the function to have child windows").
  - p5, PRINTED fact: `class_attribute(子ウィンドウを持つための機能を提供する, as_superior).` The attribute text comes from the manual.
- **Method table fact** (PRINTED, p12/folio 65): `class_method(as_graphics, draw_line, [5, object, x1, y1, x2, y2])`, i.e. `:draw_line(Obj,X1,Y1,X2,Y2)` = draw_line/5.
  - `as_graphics` also has `:draw_circle` and `:draw_rectangle` (PROSE).
  - VARIANT: held programs use `standard_io_window` draw_line/7 and draw_line/8 (requirements.tsv). Those are probably the line-width, style and op variants; WINCS's own table may have abbreviated.
- **Fig.5 "synthesized classes"** (PRINTED, p12; generated code, short):
  - header line `@@psi000::>sys>user>wincs>wincs>finished.esp.5`;
  - `my_window1` nature: `with_margin, with_label, with_border, as_superior, as_input_buffer, inferior_window`;
  - `my_window2` nature: `with_margin, with_label, with_border, as_scroll, as_output, as_graphics, as_markers, as_input, as_mouse_input, inferior_window`;
  - `my_window3` nature: `with_margin, with_label, with_border, as_menu, as_single_select, as_mouse_input, inferior_window`.
  - These show the canonical ORDER of window natures: sash mixins (`with_*`) first, then the `as_*` function mixins, then the base class last.
- **Fig.2 "window attribute menu"** (SCREENSHOT, p5, eyed at 400 dpi). This is WINCS's own UI, but it groups the SIMPOS classes into three kinds (TRANSLATION):
  - **base classes** (基本クラス): hierarchical window (階層ウィンドウ) = `inferior_window`; temporary window = `temporary_window`; popup window = `popup_window`;
  - **parent-window classes** (親ウィンドウクラス): shared between processes (プロセス間共有; INFERENCE: `shared_window`, named on p7); has child windows = `as_superior`; set child-window size; show icon;
  - **sash classes** (サッシクラス): show a border = `with_border`; show a label = `with_label`; **show 2 labels**; set the margin = `with_margin`;
  - buttons `DO_IT` and `HELP`.
  - Other windows on the same screen: `tms window` and `現在の実行状況` (current execution status). These are application UI.
- **Other class names in the text** (PROSE/PRINTED in TMS node facts, p7-9):
  - `one_window` and `shared_window`, as `construct(...)` defaults: one unsplit window vs one window split into several;
  - `as_single_select`, `as_input`, `as_input_buffer`, `as_scroll`, `as_markers`.
  - INFERENCE: `one_window` is WINCS's own node name, not necessarily a SIMPOS class.
- **Lead:** ref [12] is **"SIMPOS programming manual (II): I/O volume"** (SIMPOSプログラミング説明書(II) 入出力編), ICOT 1987. It is the source of the window-class descriptions. NOT HELD.
- **Version:** PSI II, 1989 (SIMPOS ~4.x). The class names fit the 1984 `with_border` / `with_label` mixin scheme (26580/TM-065) grown into ~40 classes.

## POSSIBLE SIMPOS CODE

1. **cil `library_utility` is probably real Librarian code** (INFERENCE, strong).
   - The class is stamped `mkpsi000::>sys>user>yasuko>UT.esp.2, 29-Jul-88`.
   - The 3J-8 author is **Kodama Yasuko** (児玉泰子), Mitsubishi Electric Computer Systems. She wrote the 1990 paper on Librarian customization, which describes "part classes" (部品クラス) and a "program interface part".
   - The natures of `library_utility` fit that description: `librarian_version`, `librarian_class_generator`, `librarian_delete`, `librarian_package`, `librarian_spy`, `librarian_reference`, `librarian_fdd`, `librarian_subroutine`.
   - Recommendation: treat it as a real SIMPOS 4.x/5.x Librarian component, not as application code.
2. **3J-8 Fig.2 `menu_list`** is the printed content of the **standard librarian initialization file** (SIMPOS 5.0, PRINTED, partial: the figure itself elides the middle with `:`).
   - It is system data, not application code.
3. **26580 (1984) window mixins** `bare_window` / `with_border` / `with_label` / `window_with_border_and_label`. These are system class bodies, but already printed in TM-061/TM-065 (pre-1.0). No new code; it is a third witness that settles which variant was earlier: it agrees with TM-061.
4. **Not SIMPOS code; listed so nobody counts them as system code:**
   - Giho 8609 `moving_window` (a printed example);
   - 36239 `bounce` / `as_demo_program` (a user demo in a screenshot);
   - Giho 8609 `eight_puzzle` (a demo in a screenshot).
   These are application code that uses the system API.

## PAGES READ

**Eyed** (rendered at 150-600 dpi and read by eye):
- **4D series (33rd conv., 1986):**
  - 114006 (4D-1) p1-2; 114007 (4D-2) p1-2; 114008 (4D-3) p1-2, figures at 300 dpi;
  - 114009 (4D-4) p1-2; 114010 (4D-5) p1-2; 114012 (4D-7) p1-2, screenshot at 300 dpi;
  - 114013 (4D-8) p1-2; 114014 (4D-9) p1-2; 114016 (4D-11) p1-2; 114017 (4D-12) p1-2.
- **SIG-DPS 36239:** all 8 pages; every screenshot at 600 dpi.
- **40th conv. (1990):** 118681 (3J-8) p1-2, figures at 300 dpi; 118591 (7G-2) p1-2.
- **37th conv. (1988):** 115246 (4E-7) p1-2; 115247 (4E-8) p1-2; 115248 (4E-9) p1-2.
- **SIG papers:** 26580 p1, 4, 5, 7, 8, 9; 24478 p2-5.
- **Mitsubishi Giho:**
  - 8609 PDF p15, p16 (Fig.8 at 300 dpi), p19, p20 (Fig.8-10 at 300 dpi);
  - 8907 PDF p34 (right column, 200 dpi), p35 (100 dpi).
- **FSTJ** V26N01 PDF p99 (100 dpi; status bar at 400 dpi).
- **Giho, eyed after the first pass:** giho_8810 PDF p46-47 (100 dpi); 9106 PDF p86 (Table 2, 100 dpi); 8707 PDF p28 (100 dpi).
- **WINCS** (Computer Software 8(1) 1991): PDF p2, 3, 5 (Fig.2 menu at 400 dpi), 7, 8, 12 (Fig.5 code), all at 140 dpi; the other pages are tesseract jpn OCR only.
- **Triage:** page 1 of all 31 un-catalogued IPSJ PDFs was OCR'd and then checked by eye.

**Text layer or OCR only:**
- 26580 p2, 3, 6, 10;
- giho_8810 p43-45, 48 (text layer);
- Giho 9106 p80-85, 87 (text layer, poor quality);
- Giho 8707 p27 (text layer);
- Giho 8609 p10-24 except the pages eyed above;
- FGCS84 84eRandD-5 (tesseract, all 12 pp; = ICOT TR-087, already in the TR/TM series, so not extracted);
- page 1 (top third) of every FGCS 84/88/92/94 English proceedings paper (310 PDFs: FGCS84en-proc, FGCS88en-proc1/2, FGCS92en-proc1/2, FGCS94en-proc), for titles; the 88 proc3 titles came from the held index html;
- 115300 / 116517 / 120507 / 4701 (page 1 OCR).

## OPEN QUESTIONS

1. **Librarian menu, Apr 1986.** Does it already have `Utility`? The box is cut off in Giho 8609 Fig.8. 36239 (Sep 1986) has it.
2. **Number in the librarian window title.** In `librarian 48 (default: user)` / `librarian 49`, is the number a process number or an instance number? Compare `librarian_1`, `debugger_1` and `pmacs_1` in 1986, which look like `<class>_<instance-no>`; 1990 uses a space.
3. **Window label forms.** `editor_main_window/5`, `mt_utility_window/3` and `talk_input_window/?` (`class/n`) differ from `pmacs_1` (`name_n`). Are these two naming schemes, one for windows without a title and one for subsystem windows?
4. **Debugger trace ports and menu.**
   - Apr 1986 shows the ports CALL/EXIT with the prefixes `new>` and `builtin>`; Sep 1986 adds `unify>` and `pick>`. Which prefixes exist in 3.0+?
   - The menu items Method / Step / Skip / Leap / Fail / Retry / No trace / PREDICATE / clause: what do `Method` and `PREDICATE`/`clause` mean (a toggle of the trace granularity?).
5. **"SIMPOS II B00"** (Mitsubishi, 1989): which ICOT version is it (4.x?)?
6. **Missing print and network classes.** `virtual_printer`, `printer_spooler` and `as_spooler` (1986) are absent from the held partitions. Were they renamed, or never used by the held programs?
7. **Network methods.** Giho 8907 names `connect` / `send` / `receive`. Are these the `tcpip_socket` method names, and with what arity?
8. **Not held, and the best leads to chase.** The first is the best: "SIMPOSプログラミング説明書(II) 入出力編" (SIMPOS programming manual II, I/O volume), ICOT 1987, cited by WINCS as the source of its window-class descriptions. Others:
   - IPSJ 29th conv. 4E-6 "SIMPOS window subsystem" (Iima, 1984);
   - IPSJ 30th conv. kana-kanji (Fujimaki et al., 1985); Hattori 29th conv. pp285-304; Kurokawa 30th conv. pp295-316;
   - Ishibashi, Computer System Symposium, Dec 1985;
   - 4D-6 and 4D-10;
   - "小型化PSI/SIMPOS操作説明書 基本編 (SIMPOS 5.0)" ICOT 1988;
   - CiNii records: SIMPOS使用説明書 MP3001-1 (1985.4), SIMPOS操作説明書 MP3002-1 (1985.4), "SIMPOS(1.5版)機能追加・変更点の説明資料" SIM-I-U-GEN021 (1985.9).

## CHECKED, NOTHING (on window / librarian / shell topics)

**IPSJ:**
- The non-SIMPOS groups in the triage list: CHI, Toshiba IP1704, Multi-PSI hardware, PIM/KL1/PIMOS (including 115119, which is the PIMOS shell), PSI hardware and firmware.
- 115300, 116517, 120507: Common ESP, the language only.
- 4701: a magazine survey of PSI architecture; no UI.

**FGCS proceedings** (page-1 title OCR of 310 PDFs):
- The only PSI/SIMPOS/ESP papers are 84eANGC2-1 and 84eANGC2-2 (PSI hardware and microinterpreter), 84eLPLM1-4 (= TM-055, ESP), and 84eRandD-4/-5 (= TR-086 and TR-087).
- RandD84en-rpt 84e005 and 84e006 are the same two reports; they are held in the TR series and outside this scope.
- 88/92/94: only PIMOS / KL1 papers; nothing on SIMPOS.
- FGCS88jp-demo index: demos of applications only.

**theses:**
- Nakashima D-thesis: SIMPOS is mentioned only in passing (PSI performance; a window evaluation at the 34180 text line is hardware performance).
- The Ohno and Rokusawa theses: nothing.

**journals:**
- Mitsubishi Giho 8412, 8512, 8612, 8712, 8802 (PSI-II hardware; no SIMPOS UI), 8805 (the word "menu" only), 8812, 8901, 8912, 9012, 9111, 9112, 9206, 9212, 9312, 9412: no SIMPOS.
- giho-9103 pp.105-108: 4 passing mentions.
- FSTJ V24-V29: nothing, except V26N01 (ExReps; see the per-item notes). V29N02's "PSI" hits are only Multi-PSI references in a bibliography.
- J-STAGE: sicejl 25_4_355 (Yokota & Uchida, "inference machines", 1986), jjsai 2_441 (Yokota, sequential Prolog machines), 2_450 (Uchida, parallel inference machines), 4_265 (PIM) and 8_159 were grepped for SIMPOS, ＳＩＭＰＯＳ, ウインドウ/ウィンドウ, メニュー and ライブラリアン: zero hits in each. They are hardware surveys.
- WINCS 8_1_54 is RELEVANT; see its per-item notes.

**NOT CHECKED (no time):**
- the FGCS jp-rpt, en-rpt, jp-demo (except the 88 demo index), jp-out, workshop and ps volumes;
- the FGCS92jp-demo index.

**web:**
- 23 pages mention SIMPOS. They are museum or history prose only (museum.ipsj.or.jp 0009; airc HISTORY 84-2, 88, 88-2, 90, 92, 93; IFS newsletters 04/05; IFS abstracts 003/004; cesp-E; ICOT Journal 07 TOC; MITIrr doc114/119; the CMU ai-repository index).
- 3 CiNii book records give leads only (above).
- No menus, classes or screenshots in any of them.
