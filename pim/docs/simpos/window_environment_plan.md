# A SIMPOS windowing environment on the model: the plan (2026-11-25)

The owner asked what it would take to get a full windowing terminal environment that replicates
SIMPOS, using what we already know. This page answers that. It is a plan, not an implementation.

The environment covers:
- the PSI's bitmap screen and the status line;
- SIMPOS windows, menus, the system menu and the window manipulator;
- the mouse and the keyboard;
- standard-I/O text windows and Pmacs.

It has to be driven by the held SIMPOS-side code (`pimfep`, `pimscsi` and the IFS applications)
running on our kl0/espc model (`../../psi/`), through the stand-ins in `../../psi/standin/`.

It builds on these sources and does not repeat them:
- `subsystems/window.md`: the graded specification of every window class, selector, option and
  event code. Section numbers below are that page's, written "W§n".
- `subsystems/shell.md`: the system menu and the Coordinator.
- `subsystems/librarian.md`.
- `boot_route.md`: boot now reaches the system menu and a started Login PIMOS prompt.
- `../fep_services.md` §2.6, §6.8-6.9 and §7.3: the FEP window commands and the login dialogue.
- `../../psi/README.md`: steps 3a-3l.

The evidence grades are those of `window.md` §0.1: PRINTED, PRINTED-INTERFACE, PROSE, SCREENSHOT,
USAGE and INFERENCE. MEASURED marks a number this session re-ran.

---

## 0. The answer in one page

**What is held.**
- The interface the held programs need is well documented:
  - 194 distinct window selectors are required;
  - 93.9% of 7,162 window uses have some evidence (W§8);
  - the FEP route's own needs are a short list (§2.1).
- **The fonts the route asks for are held and readable** (§1.4, new this session). `font:test_11.font`,
  which the Login PIMOS window and PIMOS's console both name, is in the HELD psdpim archive. Its
  `f822` format decodes byte-exactly: 128 glyphs on an 11×14 cell, JIS rows 21 and 23.
- There is a printed precedent for the architecture. On the PSI/UX, the SIMPOS window manager
  stayed in SIMPOS, and an external "SIMPOS window server" drew the whole SIMPOS screen in one X
  window. Window control, mouse and keyboard were still handled by SIMPOS (Giho 9106 p86; IPSJ
  SIG-ARC 24478).

**What is lost.**
- No window-system class body survives (W§0.3).
- The display handler is lost.
- The kana-kanji converter is lost.
- Pmacs's default key bindings are lost.
- No kanji font and no `font_13` is held.

So every window class we run is a labelled stand-in, built from W§2-§4.

**Recommendation.**
1. The window classes stay ESP stand-ins in package `simpos`. Held classes subclass them and put
   `before:`/`after:` demons on their primaries (W§2.12), so they must be in the inheritance order.
2. Under them sits one narrow device layer, written in Python through the existing
   `SIMPOS_MODELS` hook in `../../psi/kl0.py`. It has a 1-bit framebuffer, a handful of drawing
   primitives and an event queue. It is our "window server", as on the PSI/UX.
3. Everything you see is derived from the one framebuffer, plus a character-grid shadow of it:
   - first a terminal transcript;
   - then PNGs at the real resolution;
   - then a live view in a browser canvas.
   This needs only the standard library, so no SDL.
4. Input is a scripted, replayable event list. An event is injected only when every process is
   waiting. It enters at the Coordinator's printed translation table (TR-046 p28).

**Target.** SIMPOS as the held programs see it:
- the 1991-94 `.ptf` packages and the 3.x-7.x IFS sources;
- a monochrome screen 1280 dots wide, with a 1280×944 drawing area (§1.1);
- the look of the 2.50/A00 video and the 4.2 FSTJ figure (§3).

Mixing a late code base with an earlier look is an anachronism we choose on purpose: no screen
image of 5.x-7.x SIMPOS is held. The resolution is a parameter. The Oki PSI-II's 1600 is another
legal value (W§2.13).

**Milestones** (§5) follow the held route's next stops, in this order:
- M1: keyboard into the login requester;
- M2: its menus;
- M3: the `pmacs_window` text protocol behind PIMOS's window device;
- M4: the PIMOS console and the `Shell>> ` prompt;
- M5: the bitmap screen with the real font;
- then the chrome, the manipulator, graphics and the IFS applications.

---

## 1. Hardware facts to replicate

### 1.1 Display

| fact | value | grade | cite |
|---|---|---|---|
| PSI-I (1984), as designed | "1200 x 912 (or 1280 x 864)" black-and-white bitmap display | PROSE | TR-046 PDF p6 (W§4.2) |
| PSI-I (Jan 1986), ICOT's configuration | 「モノクロ 1200*900 ドット」 ("monochrome, 1200×900 dots"); the bitmap display is a Multibus (IEEE-796) device | PRINTED (handwritten figure) | TM-153 PDF p23 (`subsystems/listings/TM-153_p23_p28_recheck.txt`) |
| PSI-I, ICOT's 1986 workstation note | 1280×864 | PROSE | TM-224 p11 (folio 10) |
| **MELCOM PSI (Mitsubishi product, 1986)** | **1,280×960 dots**, multiwindow; bitmap display, keyboard, mouse and printer as standard | PROSE, page image read 2026-11-25 (the text layer garbles it to "に80×960") | Mitsubishi Denki Giho 60(9) 1986, PDF p13, folio 7 (599), and Fig. 2 (`nonlocal/lit/journals/mitsubishi_giho/8609.pdf`) **NEW** |
| SIMPOS 5.0 (1989) | default drawing size = "the screen size" = 1280/944 | PROSE | TM-785 p9, p10, p23 (W§4.2) |
| PIMOS front ends, 1992 | a full-screen window `size(1280,944)` | USAGE | kl1graph `screen.esp:25,30` (W§2.13) |
| Oki PSI-II ("O-PSI") | 1600 wide; a full-width pane `position(0,904), size(1600,216)` | USAGE | disc `exdisp.esp:35-37, 47-49` (W§2.13; which range holds which variant was not re-checked) |
| PSI-UX and "M-PSI" | 1280 wide; panes ending at y = 965 and 944 | USAGE | disc `exdisp.esp:35-37, 47-49` (W§2.13) |
| **PSI/UX (1991)** | Unix side: 1,280×1,024, 256 colours. The SIMPOS screen is one X window, "equivalent to the PSI-II display screen", inside that | PRINTED table + PROSE, page images read 2026-11-25 | Giho 65(6) 1991, PDF p88 Table 1 (82 (602)); PDF p86 (folio 80 (600)) §(3), Fig. 7 (`9106.pdf`) **NEW** |
| Depth | 1 plane = monochrome; `bmm_size` 16#07FF mono, 16#0FFF colour; on PSI/UX `get_plane_count` 1/3/4/6/8 | USAGE | paragraph `p_MAIN.esp:183-185`, `p_ux_patch.esp` (W§2.13) |
| Colour (PSI-II, 1989) | a window palette of colour pairs; one pair = a monochrome window | PROSE | Giho 8907 p34-35 (W§3.7) |
| Frame memory vs bitmap memory | the frame memory is shown; each hidden window has a save area in bitmap memory "several to several tens of times" the frame memory; restacking copies between them | PROSE (TRANSLATION) | TM-225 p10 (`subsystems/listings/TM-225_p08-11_window.txt`) |
| Bit order | MSB = leftmost dot; rows of 16-bit words; areas are multiples of 16 wide | PROSE | TM-115 p74-76, p82 (`subsystems/notes/tm115.md` W4) |

The **PSI-II's own** physical resolution is not printed in anything opened (open question Q1). The
code the replica runs asks `:get_size(#screen,W,H)` (25 uses, W§2.13), so it adapts to any size.
**Choice (INFERENCE):**
- the logical screen is 1280×944, which TM-785 and kl1graph both give;
- the status band is drawn below it, so the framebuffer is 1280×(944+S);
- S is two lines of the status font, a parameter.

### 1.2 Keyboard

| fact | grade | cite |
|---|---|---|
| Keyboard and mouse hang off the **console processor** (console bus), not the Multibus | PRINTED (figure) | TM-153 PDF p23 |
| Character codes are 16-bit JIS (JIS C 6226 / X 0208); kana and kanji are used like alphanumerics; ASCII-range text is stored as full-width JIS (`#"A"` = 16#2341) | PROSE; USAGE | TR-061 p6, TM-125 p6 (`notes/trtm_window.md`); IPSJ (ipsj.md :276); `../fep_services.md` §6.9 (every login string decodes as JIS X 0208) |
| Kana-kanji conversion sits in the **keyboard handler**, below the window system; the bottom band shows romaji, then kana, then numbered candidates; `MENU(PF16) PF10=ON_OFF, PF0-PF6=MANAGE` | PROSE; SCREENSHOT | IPSJ 114007 §4, IPSJ 36239 p2; simpos.wmv@108-113 (W§4.2) |
| Function keys `pf#0`-`pf#18` (comments: `pf#8` help, `pf#9` abort); `key#` names lf, cr, del, enter, esc, tab, bs, bell, up, down, left, right, abort, help; control, meta, control_meta and keypad families | USAGE | W§3.5 (cil `cil_esp.esp:120-254`; euod `def.esp:1553-1554`) |
| The physical keyboard: a large separate unit with a numeric pad and rows of function keys | SCREENSHOT | simpos.wmv@84-89 (`notes/video.md` §1); PSI/UX photo, Giho 9106 PDF p88 Fig. 1 |
| The numeric code values of `key#`, `pf#` and `mouse#` | **not held** (gap G2) | W§3.5 |

The layout (JIS or ASCII arrangement, kana engraving) is not printed anywhere opened. It does not
matter for the replica: input arrives as JIS codes and named keys.

### 1.3 Mouse

| fact | grade | cite |
|---|---|---|
| Three buttons (Mitsubishi-branded, on a pad) | SCREENSHOT | psi.wmv@23, simpos.wmv@84-89 |
| Events: single and double click of left, middle and right = `mouse#l ll m mm r rr` | USAGE; PRINTED (`mouse#rr`) | W§3.5; TR-046 p28 |
| Double right anywhere opens the system menu | PRINTED; PROSE | TR-046 p28; TM-112 p16, p19 |
| A click goes to the shown window under the mouse cursor; keyboard input goes to the selected window | PROSE | TM-126 p7, TM-225 p11 (W§2.7) |
| Double-click timing: "hard for the system to understand double clicks if you enter a single click just afterwards" | PROSE | TM-112 p10 |
| Mouse cursor: a small arrow; shape numbers via `set_mouse_marker/2` (6 after a menu create); the numbering is unknown | SCREENSHOT; USAGE | esp.wmv@120; cal `grmenu.esp:16` |

### 1.4 Fonts (new this session: the held route font decoded)

The HELD psdpim archive (`nonlocal/psdpim.tar.Z`, in git) carries `psdpim/FONT.DIR/`. Its
`INSTALL` copies these files to `font:`, and `../../psi/simpos_fs.py` currently leaves them out:

| file | f822 header: line height?, ?, ?, nchar, strip width (bits), height | glyphs |
|---|---|---|
| `test_11.font` (and `test_11b.font`: same header and size, different bytes from offset 2181, so some glyphs differ) | 0x14, 0xe, 0xe, 128, 1408, 14 | 11×14 cell, bias 3. Codes 0-0x1f, JIS row 21 (punctuation: 2121 space, 2125 `.`, 2127 `:`, 2132 `_`, 215d `−`, 2164 `>` ...), 2330-2339 digits, 2341-235a, 2361-237a letters, 0xffff |
| `test_10.font` | 0x12, 0xe, 0xb, 127, 1270, 11 | codes 0 .. 237a |
| `tiny_7.font` | 0xd, 0xa, 9, 127, 912, 9 | codes 0 .. 237a |
| `performance.font` | 0x28 ×3, 17, 680, 40 | 17 large glyphs (meters) |
| `csppestate.font` | 0x11 ×3, 211, 3587, 17 | 211 glyphs (CSP PE-state display) |
| `csp.icon` | header `0050 0050 0190`: 80×80, 400 words | a bordered 80×80 icon (rendered; it is the CSP's) |

**The decode is MEASURED** (2026-11-25):
- The file length equals 21 header words + nchar × 8 record words + height × ⌈width/16⌉ strip
  words, exactly, for all six fonts.
- `test_11` 'A' (16#2341, record x = 825) renders as a clean 11×14 capital A.
- 'g' (16#2367) renders with its descender.

This confirms the layout `notes/tm115.md` §(a) worked out by hand from gog-esp's `suuji.font`:
- 8-word records (code, x, y, width, height, bias, 0, 0);
- one horizontal strip of glyphs;
- rows padded on the right;
- MSB leftmost.

Recipe (stdlib only; run on the extracted file):

```
python3 -I -c "import struct,sys; b=open(sys.argv[1],'rb').read(); w=struct.unpack('>%dH'%(len(b)//2),b); n=w[4]; wpr=(w[5]+15)//16; base=21+8*n; assert len(w)==base+w[6]*wpr; r={w[21+8*i]:w[22+8*i:26+8*i] for i in range(n)}; x,y,W,H=r[0x2341]; print('\n'.join(''.join('#' if w[base+(y+j)*wpr+(x+i)//16]>>(15-(x+i)%16)&1 else '.' for i in range(W)) for j in range(H)))" test_11.font
```

What this gives the replica:
- every character of the Login PIMOS dialogue in its real glyph. `../fep_services.md` §6.9 lists
  the JIS codes of the prompts, and all are in `test_11`;
- the same for the PIMOS console, which `login.kl1` creates with `"font:test_11.font"`
  (`../fep_services.md` §7.3 row 7).

**Not held:**
- `font_13`, the 13×19 default (TM-125 p20; TM-115 p27);
- every kanji and kana font (`kanji_16`, `kanji_24`, `kanji_28`; W§3.6);
- the label fonts `ank_24`/`kanji_24`;
- the status-line font.

The 32-bit `.font` family of kappa2, euod and fuzclust is held but not decoded (gap G9).

**Substitutes (OURS, labelled on screen in the test transcript):**
- `font_13`: `test_11` scaled into a 13×19 cell (the glyph centred, not stretched);
- kanji/kana: a visible "missing glyph" box, so a gap is never silent. Optionally a host
  Unicode rendering in the terminal stage only, through Python's `euc_jp` codec.

### 1.5 How the PSI drew: what KL0 offers

**Negative finding (MEASURED 2026-11-25).** No bitmap or raster built-in appears in:
- `../../psi/kl0_opcodes.tsv`: its draw-related rows are paragraph witnesses for ordinary opcodes;
- cil's KL0 built-in wrapper list, 194 `is_builtin` names (`cil/src/cil_kl0.esp`, held IFS);
- `required/builtins.tsv`: 490 rows, none graphical.

The KL0 primitives that touch bits in bulk are the string ones:
- `and_`, `or_`, `xor_` and `complement_string(_elements)`;
- `copy_string_elements`, `move_string_elements`.

In held code they are used for data, not pixels. gog-esp's 48 `xor_string_elements` clear Go-board
flag strings (`FAMILY.ESP:186`, `LAMOVE.ESP:117`).

The machine-level names are `physical_word/3`, `set_physical_word/3`, `special_function/2` and
`bus_reset`. Together with TM-153's figure (the bitmap display is a Multibus device) and TM-115's
manager/user split (W§2.5: in 1.0 only the window manager touches bitmap memory), they suggest:
- the window manager drove a display controller over the I/O bus;
- the rasterop was done there, or in microcode, not by a KL0 instruction.

That is **INFERENCE**, and nothing on the route depends on it. The replica draws in the device
layer (§4.2).

---

## 2. The class and selector shortlist

### 2.1 What the FEP route needs: measured on the held packages

`python3 -I psi/kl0.py census --fep` and `--fep --recipes` were re-run 2026-11-25 on this tree. The
results match the step 3l figures in `../../psi/README.md`:
- plain: 802 success, 234 failure, 413 refused;
- recipes: 829, 235, 385.

These are the window-system stops (the "simpos## calls" list):

| stop | plain | recipes | class it lands on | evidence for the method |
|---|---|---|---|---|
| `pimfep##pimos_window:get_interpreter/2` | — | 5 | pmacs_window | USAGE (W§2.11) |
| `pimfep##pimos_window:has_been_reshaped/1` | — | 4 | pmacs_window / reshape_notifier | USAGE (demons, W§2.12) |
| `simpos##pmacs_window:putl/2` | 3 | 3 | pmacs_window, the §2.4 protocol | PRINTED Giho 8609 p20 (putl/2); USAGE |
| `pimfep##as_pimos_login_requester:read/4` | 2 | 2 | standard_io_window `read/2`, `getl/2`, `inhibit_echo/1` | USAGE |
| `pimfep##pimos_window_editor:carriage_return/1` | 1 | 1 | standard_editor (demons prove the primary) | USAGE (W§2.12) |
| `simpos##standard_temporary_menu:create/3` | 1 | — | menus | PRINTED-INTERFACE TM-125 p13-14 |
| `simpos##editor_text_buffer:get_buffer_instance/3` | 1 | 1 | editor buffer pool | USAGE |
| `simpos##messenger:show/2`, `ascii_coder:to_kanji/3`, `telnet_terminal:create/2` | 1 each | 1 each | shell and network side | `shell.md` |

The whole window surface `pimfep` references is in `subsystems/notes/ptf.tsv`, the rows citing
pimfep (read 2026-11-25). It is small:

| class | members referenced by pimfep |
|---|---|
| `pmacs_window` | c:create/3; beep/1, flash/1, get_font/2, get_interpreter/2, get_text_size/3, get_title/2, has_been_reshaped/1, reshape/5, set_input_buffer/2, set_size/3, set_text_size/3, set_title/2; slots `activity`, `original_buffer`; options position, size, title |
| `standard_editor` | get_window/2, carriage_return/1 (as nature of `pimos_window_editor`) |
| `editor_text_buffer` | c:get_buffer_instance/3 |
| `standard_io_window` | c:create/3, options nature, position, size; plus what `read/4` sends (W§2.4) |
| `standard_menu`, `standard_temporary_menu`, `standard_scrolling_menu` | c:create/3 with items_list, label_flag; read/2, get_size/3 |
| `standard_choice_window` | c:create/3 with choice_list, label_flag |
| `standard_window` | close/1, erase_cursor/1, hide/1, read/2, set_position/3 |
| `font` | c:create/3, pathname/2 |
| `screen` | c:get_size/3 |
| `image_file` | c:load/5 |
| `as_mouse_input` | `mouse#l ll m mm r rr` (the supervisor's dispatch, W§3.5) |

`pimscsi` references only `pmacs_window` and `standard_io_window`.

On the PIMOS side, the window device is driven by 24 FEP commands (`../fep_services.md` §2.6, 104
to 146). Every one lands on a `pimos_window_editor` method, and each of those sends the
`pmacs_window` methods above (§6.8: "the window is a PMACS editor buffer").

**So the FEP route needs about 40 selectors on 11 classes**, against the 194 the IFS applications
need.

### 2.2 What the IFS applications need: ranked by use (from W§2.14, W§8)

Top classes by held use (counts are W§2.14's, generated by `subsystems/tools/window_appendix_gen.py`):

| rank | class | top selectors (uses) | best grade of the interface |
|---|---|---|---|
| 1 | `standard_io_window` | putl/2 220, c:create/3 149, kill/1 110, show/1 78, set_font/2 77, draw_line/7 55, activate/1 55 | PRINTED-INTERFACE (TM-125) for life cycle; USAGE for putf/putt/getl |
| 2 | `standard_io_buffer` | c:create/2 124, putf/3 154, getl/2 96, putt/2 74 | PRINTED (1990 ESP manual example) |
| 3 | `standard_output_file`, `standard_input_file` | c:create/3 106/145, putf/3 142, close_input/1 133 | USAGE |
| 4 | `font` | c:create/3 220 | PRINTED TM-785 p37 |
| 5 | `inferior_window` | c:create/3 177, get_size/3 42 | PROSE WINCS; PRINTED-INTERFACE TM-125 |
| 6 | `standard_menu` | activate/1 101, read/2 88, c:create/3 51 | PRINTED-INTERFACE TM-125 p13-18 |
| 7 | `pmacs_window` | c:create/3 75, activate/1 50, putf/3 47, set_font/2 41, flash/1 26 | USAGE |
| 8 | `standard_temporary_menu`, `temporary_menu` | c:create/3 64/72, read/2 40/31, kill/1 43 | PRINTED-INTERFACE |
| 9 | `standard_editor`, `pmacs_standard_editor` | get_window/2 126/62, current_buffer/2 42/88 | USAGE |
| 10 | `standard_superior_window`, `essential_window`, `editor_text_buffer`, `window_without_label`, `standard_scrolling_menu`, `standard_window` | create/3, geometry, draw_* | mixed; draw_* PRINTED-INTERFACE (TM-125 p17, TM-785 p40) |

Coverage (W§8): of 676 required methods carrying 7,162 uses:
- 61.3% of the uses are documented (PRINTED or PRINTED-INTERFACE, owner stated or not);
- 93.9% have some evidence;
- 56 selectors are UNSPECIFIED, with no meaning-bearing evidence.

**Printed bodies:** only `bare_window`, `with_border` and `with_label` (TM-065 p15-16, 1984) and the
1984 `default_translation_table` (TR-046 p28). Every composite class's body is INFERENCE.

---

## 3. The look: every image held, and what it shows

All of these are SCREENSHOT grade, and each is in `nonlocal/lit/` on disk.

| image | version | what it shows | notes file |
|---|---|---|---|
| ICOT museum video, simpos.wmv @0-10, @9.6-11.3, @49-62, @108-118, @124-137 | A00 (with esp.wmv) | `debugger_1` with `?- █`; the two-column SYSTEM MENU (items read in `notes/video.md` §3); the program → `create`/`kill` → rubber-band dialogue; kana-kanji in the bottom band; the window manipulator menu `SHOW HIDE RESHAPE MOVE EXPAND MENU PERM… ATT…`; the Debugger Menu; the librarian command column | `subsystems/notes/video.md` |
| esp.wmv @108-169 | A00 | Pmacs mode line `PMACS(esp)(87,26) *-1* …`, echo line `Visit File(move_win.esp):`; status band `USER : demo` / `SIMPOS Version A00`; the black `move_win` window; the multi-select `Select files` menu with reverse-video choices and `Do it` | video.md §2, §5 |
| melco.wmv @50-60, @147-158 | 2.50 | status band `USER : KCM` / `SIMPOS Version 2.50`; bottom labels (`Action_Window`) | video.md §1-2 |
| psi.wmv, icot.wmv | PSI-I | hardware: cabinet, CRT, keyboard, 3-button mouse | video.md §1 |
| TM-153 PDF p28 Fig. 7 | 2.00, 25-Jan-86 | full screen: status line two rows (`USER :`, `SIMPOS Version 2.00`, `SWAPPED`, `spool`, date); top labels and a bottom label (`editor_1`); EDIPS mode line; the `network` multi-column menu with column heads; graphics windows | `subsystems/listings/TM-153_p23_p28_recheck.txt` |
| TM-115 p25-26, TM-112 p25 | 1.00 | the font editor's 17 windows; status line `USER : me` / `SIMPOS Version 1.00` / reverse field / `23-May-85 Thursday 20:22:44`; multi-column menus | `notes/tm115.md` W7 |
| TM-125 PDF p7 Fig. 4, p10 Fig. 5 | 1.0 | the ATTRIBUTE choice window; label strip, margin, border diagram | `notes/trtm_window.md` |
| TM-134 p67-71 | 1.0 | shell/debugger dialogue `> Success !!` | `notes/trtm_progsys.md` |
| IPSJ 36239 p5-6 | 2.50 | Pmacs with mode line `[48,17]`; EDITOR MENU; the `KANAKAN` candidate pop-up in `pmacs_4`; a graphics window with marker | `notes/ipsj.md` |
| IPSJ 114012 Fig. 2 | 1987 | document processing in `editor_main_window` | ipsj.md |
| Giho 8609 Fig. 8, Fig. 10 | 2.x | ESP window program and its run (`Input X>100.`) | ipsj.md |
| FSTJ 26(1) p99 Fig. 9 | 4.2, 1989 | status band `USER : demo` / `SIMPOS Version 4.2`, `screen` / `editor_buffer_window/19`, `SWAPPED`, `spool`, `12-Sep-89 Tuesday 10:25:41` | ipsj.md |
| TM-785 p10-26 | 5.0 | dialogue look, colour-pair windows | `notes/trtm_manuals.md` |
| Giho 9106 PDF p88 Fig. 1 | PSI/UX 1991 | photo: a colour screen with windows; keyboard; mouse on a pad (too small to read) | this page §1 |

**The common look, taken from these** (W§4.2-4.5):
- white background, black text;
- overlapping windows with thin single-line borders (2 dots by default) and no shadows;
- the label strip inside the top border, under a rule, with the name left-aligned (bottom labels
  exist);
- the status line a black band of two rows at the bottom:
  - row 1 `USER : name`;
  - row 2 `SIMPOS Version v`;
  - a reverse box naming the selected window;
  - on the right `SWAPPED`, `spool` and the date;
- pop-up menus with a title bar and centred items; the item under the mouse boxed (2.50/A00), not
  inverted (1.0);
- a solid block text cursor and an arrow mouse cursor;
- Pmacs: text pane, then the reverse mode line, then the echo line.

**Window names.** Two forms are seen: `<prog>_<n>` (video) and `<class>/<n>` (TM-112, FSTJ). The
replica uses `<class>/<n>` for the status box and the program's own title for the label
(INFERENCE; W Appendix B).

---

## 4. Architecture

### 4.1 Where the window system lives

```
 held ESP (pimfep, pimscsi, IFS apps)        e.g. pimos_login_requester, pimos_window (< pmacs_window)
          |  ESP sends
 stand-in ESP classes, package simpos       standard_io_window, pmacs_window, standard_editor,
 (psi/standin/*.esp, labelled)              menus, choice windows, screen, font, coordinator,
          |                                 window_manager (one process, OURS)
          |  a few SIMPOS_MODELS entries (OURS, Python)
 device layer (Python, new file)            framebuffer 1bpp; fill/line/blit/copy-area/xor;
 "the window server"                        glyph cache from FONT.DIR; event queue; renderers
          |
   renderers: text transcript | PNG (stdlib zlib) | browser canvas (static HTML, polling)
```

**The stand-ins stay ESP**, for three reasons:
1. The held code subclasses SIMPOS window classes: `pimos_window` < `pmacs_window`;
   `pimos_window_editor` < `standard_editor`.
2. It hangs demons on their primaries (W§2.12). Those demons only run if the primary is an ESP
   method in the linearisation that espc builds.
3. It also reads their slots (`activity`, `original_buffer`).

A Python-only window would bypass all of this.

**Python sits below a small, fixed primitive set.** This is what the PSI/UX did: SIMPOS's window
manager parsed requests and generated drawing commands, and a "SIMPOS window server" outside SIMPOS
drew them (IPSJ SIG-ARC 24478; Giho 9106 p86, PROSE). The primitives, each one OURS:

| primitive | arguments | used for |
|---|---|---|
| `fb_fill` | rect, op (set/reset/xor) | clear, borders, reverse video, status band |
| `fb_line` | x1,y1,x2,y2, width, style, op | `draw_line/5-8`, rectangles |
| `fb_glyph` | font, JIS code, x, y, op | every text path (`write`, `putl`, labels, menus) |
| `fb_copy` | src rect → dst, op | scroll, `transfer/8`, save areas, menus over windows |
| `fb_save` / `fb_restore` | window id | the save areas of TM-225 p10 |
| `ev_next` | → event or none | keyboard and mouse into the handler stream |
| `font_load` | path → metrics | `font:create/3` (the stand-in now ignores the file) |

They are reached as `SIMPOS_MODELS` entries on one OURS class, say `simpos##bitmap_display`. It is
a real SIMPOS class name: `get_mouse/2` is sent to it (USAGE, W§2.13). It gets OURS selectors,
labelled as such. No new KL0 opcode is invented: §1.5 found none to model.

**Clipping and overlap.** In the stand-in window manager:
- every window has a save area;
- only fully shown windows draw into the framebuffer;
- output permission `out` and `show` are honoured. Held code uses only those two (W§4.1);
  `wait` and `notify` refuse.

### 4.2 Rendering target

**Recommendation: one framebuffer, three views, all standard library.**

1. **Text transcript** (stage 1). A character-grid shadow kept by the same stand-ins: each text
   window is a grid of JIS codes, decoded to Unicode with the `iso2022_jp`/`euc_jp` codec for
   printing. It is dumped as an ASCII-boxed screen per event step. This is what the tests compare,
   and it is the cheapest discriminating check.
2. **PNG at the real resolution** (stage 2). The 1bpp framebuffer is written with `zlib` + `struct`
   at 1280×(944+S). It is deterministic, so a test can pin a SHA-256 or a pixel count per frame.
3. **Live view** (stage 3). A static HTML page whose canvas polls the latest frame from
   `python3 -m http.server` in a scratch directory. Keyboard and mouse go back as POSTs into the
   event queue.
   - No SDL or pygame: the repo has no GUI dependency now, and adding one buys nothing a canvas
     lacks.
   - A curses front end over the text grid is a cheap alternative for terminal use.

### 4.3 The event path

```
 scripted events / live input ──> device layer queue
      (OURS: {key, JIS}, {key, name}, {mouse, Button, X, Y}, {move, X, Y})
      │  delivered only when every process waits (the pump, OURS)
      ▼
 keyboard/mouse handler process (stand-in for the lost B4 handlers; one process, OURS)
      │  `put` on the coordinator's event stream
      ▼
 coordinator: default_translation_table (PRINTED TR-046 p28; TR-061 p13)
      ├─ mouse#rr, control#"s"  → invoke_system_menu      (already modelled, step 3l)
      ├─ mouse#l on a window    → visit (select it)
      ├─ control#"k"/"l"/"a"    → kill / lull / arouse the window's process
      └─ default: pass-through  → the selected window's input stream (key) or the window under the
                                  mouse (click), as {Code} or {Source,Data,Cmd,X,Y} for read/6
```

- **The pump.** `../../psi/kl0.py` already runs several processes under the supervisor and
  reaches a state where every process waits (boot_route §4.4). The pump is a loop: run until
  quiescent, deliver one event, repeat. The run is deterministic and the event list replays.
- **Echo and line editing.** In `standard_io_window` these are OURS. In `pmacs_window` they come
  from Pmacs: the editor buffer holds the echo, and `carriage_return/1` ends a line, its demons
  proved in pimfep (W§2.11-2.12).
- **Interrupts.** A `{Id, 3}` reply on PIMOS's window device is control-C, the window's attention
  (`../fep_services.md` §2.6). `mouse#mm`, `control#"c"` and `key#abort` are what
  `read_sense/2`-polling code stops on (W§2.7).

### 4.4 How it joins Login PIMOS → FEP → PIMOS

1. **Login PIMOS** (now: it waits in `read/2` after its first prompt).
   - The keyboard path delivers lines into its `standard_io_window`.
   - It then runs the held `feps_menu/2`, `check_code/4` and `getl/2`, the user-name prompt, and
     the password with `inhibit_echo/1` (boot_route §5 item 1).
   - The menus `PIMOS FEPs` and `PIMOS USERs` are `standard_temporary_menu`s read from
     `me:pimos.feps` and `me:pimos.uids` (`../fep_services.md` §6.9).
2. **The login request** goes over the held remote-login classes.
   - A local login is `"local"`.
   - The PIMOS side's texts come back and are `putl`'d into the same window: "Your request is
     accepted.", "Login procedure starts.", "OK. Your initial program starts.", "Good luck!".
3. **PIMOS's windows** arrive as FEP window commands. Their order is in `../fep_services.md` §7.3
   rows 7 and 13:
   - 104 create, then 127 reshape `(200,200,47,14)`, 130 title `"PIMOS CONSOLE"`, 132 font
     `"font:test_11.font"`, 143 show;
   - later 111 putb `"Shell>> "`, 112 flush, 110 getl.

   Each command reaches `pimos_window_editor` and then `pmacs_window` (§6.8). So the PIMOS console
   is a 47×14-character Pmacs window in test_11, at (200,200).
4. **What answers the FEP commands** is still two things:
   - the held `pimfep` on our kl0 (the PSI side);
   - and, for whole-system runs, `../../ref/pimm/fep.py` (the Python FEP stand-in).

   The windowing environment needs no change to either protocol: it only gives `pmacs_window` a
   body.

---

## 5. Milestones

Each milestone:
- is a test in `../../psi/test_espc.py`, named below;
- states what it proves;
- names the injected bug that must make it fail (AGENTS.md "How work is verified here" 2; the
  observed failure set goes in the test header).

Sizes are rough, counted in lines of ESP stand-in plus Python, and include the tests.

| # | milestone | test, and what it proves | discriminating injection | size |
|---|---|---|---|---|
| M0 | **Fonts placed and read.** `simpos_fs.py` places the 7 FONT.DIR files; `font:create/3` loads metrics through `font_load` | `test_win_m0_font`: `test_11`'s header (128 glyphs, 11×14), the 'A' bitmap's 48 set dots at 16#2341 (MEASURED with the §1.4 recipe); a missing font fails `create/3` (INFERENCE: the held fallback-on-failure evidence is for `standard_input_file`, not `font`) | swap the record's x and y fields: the A test fails | ~120 |
| M1 | **Keyboard into Login PIMOS.** Event pump, the handler process, the coordinator's pass-through, `standard_io_window` `getl/2`, `inhibit_echo/1`, `permit_echo/1`, character read to code 13 | `test_win_m1_login_keys`: the scripted lines `local`, a user, a password take the held requester past its three prompts; the transcript shows the prompts, the echoed name and **no** echoed password; `exit` ends it | make `inhibit_echo/1` a no-op: only the password-echo check fails | ~250 |
| M2 | **The login menus.** `standard_temporary_menu` create/read with items_list, `abort`, the JIS-space trigger | `test_win_m2_feps_menu`: a 16#2121 first character opens `PIMOS FEPs`; a scripted click on `local` returns it; leaving the menu returns `abort` | return the item label instead of its Value: the selection check fails | ~200 |
| M3 | **pmacs_window's text protocol** (the census stops of §2.1): putl, putb, getl, flash, beep, set/get_title, set_font, reshape/5, set/get_text_size, get_interpreter, has_been_reshaped, editor_text_buffer get_buffer_instance | `test_win_m3_pmacs`: the recipe census moves the 5 + 4 `pimos_window` rows and the 3 `putl/2` rows from refused (MEASURED baseline 829/235/385) and none moves backwards; a window made by the held `create_pimos_window/3` shows a putl'd line and returns a getl'd one | have `get_interpreter/2` answer the editor, not the interpreter: the get_interpreter rows refuse again | ~400 |
| M4 | **PIMOS console and `Shell>> `.** The FEP window commands 104 → 127 → 130 → 132 → 143, then 111/112/110, through held `pimos_window_editor` into M3 | `test_win_m4_console`: the transcript shows a 47×14 window titled `PIMOS CONSOLE` at (200,200) in test_11, holding `Shell>> `, and a typed line comes back as `{W,1,Line}` | drop 132's font: the font check fails | ~250 |
| M5 | **The bitmap screen.** The device layer (§4.1), the PNG writer, borders, labels, the text cursor, the status band from the test_11 glyphs | `test_win_m5_png`: the M1 and M4 screens rendered at 1280×944(+S); exact dot counts for one glyph run and one border; a PNG decoded back to the same framebuffer | draw borders 1 dot wide: the border dot count fails | ~400 |
| M6 | **Screen chrome and system menu.** The status line, the `<class>/<n>` box and the date; the SYSTEM MENU as a two-column pop-up from login.com's items; `create`/`kill` and rubber-band placement; selection by `mouse#l` | `test_win_m6_chrome`: `mouse#rr` draws the menu at the mouse; a click on `Login PIMOS` starts it (step 3l's path, now by mouse); the status box names the selected window | route `mouse#l` to the window under the previously selected one: the selection test fails | ~350 |
| M7 | **The window manipulator** (TM-125 p8 items; video), restacking with save areas, `out`/`show` permission | `test_win_m7_manip`: HIDE then SHOW restores a covered window's dots exactly; MOVE and RESHAPE call the held `has_been_reshaped/1` | skip the save-area restore: the restore test fails | ~350 |
| M8 | **Graphics and markers** (W§2.5-2.6): `draw_line/5-8`, rectangles, filled shapes, `draw_string/4-6`, `transfer/8`, `copy/9`, markers, `get_mouse_position/3` | `test_win_m8_graphics`: the held paragraph `p_icon`/`g_window` draw paths (the `execute_graphics_command/2` batch, W§2.5) give pinned dot counts; XOR twice erases | make `exclusive_or` act as `set`: the erase check fails | ~500 |
| M9 | **Choice windows and the remaining menu kinds** (W§2.9-2.10, §3.3-3.4) | `test_win_m9_choice`: a held `choice_list` create (pimfep `standard_choice_window`) reads back `[{Key,Value}]` | return the default for an edited field: fails | ~350 |
| M10 | **Pmacs proper**: buffers, mode line, echo line, the EDITOR MENU, a minimal default key set (OURS, gap G6), the papyrus/cal editor subclasses | `test_win_m10_pmacs`: the held `disc/exshow.esp` sequence (create, get_editor, read_file, command_interpret) edits and saves a file in `simpos_fs` | — | ~1200 |
| M11 | **Live view and IFS applications.** The browser canvas; then IFS programs one at a time (W§7's order) once their non-window needs are met | per program, a pinned screen and transcript | — | open |

**Status (2026-11-25):** M5's device layer exists as `../../psi/winfb.py` (framebuffer, the §4.1
primitives as a frozen command stream, PBM P4, test_11 glyphs; tests `../../psi/test_winfb.py`),
written first for the hardware plan's H0.

**Status (2026-11-25, later): M0 done; M3's core and M5's window drawing done for the Login PIMOS
window, from a live run** (`../../psi/README.md` "Window M0, M3, M5"; tests `test_espc.py` class
`Window`):
- **M0.** `../../psi/simpos_fs.py` places FONT.DIR's seven files in `>sys>font` with a system
  alias `font` (the INSTALL line is HELD; the directory and alias are OURS). `font:create/3`
  retrieves the file and the device decodes it. test_11's cell is 11×14 (its space character);
  a missing file and a non-font file (`csp.icon`) fail `create/3`; test_11's 'A' is 48 dots.
- **Where the window manager lives: ESP**, as §4.1 recommends and as the PSI/UX did. The new
  stand-in `window_pane.esp` (OURS class) decides every rectangle, glyph position, scroll and
  cursor, and sends only primitives. `../../psi/windev.py` (OURS) answers them as
  `simpos##bitmap_display` `fill/6`, `glyph/6`, `copy/8`, `line/7`, `load_font/5`,
  `default_font/4` and `get_size/3`, through the `SIMPOS_MODELS` hook. Each is one command of the
  frozen winfb set on one frame per machine, and the device logs them, so **a live run's drawing
  is a winfb command stream** that replays to the same frame (and so can drive
  `bsv/WinFbBox.bsv`'s bench or, later, the UART of the hardware plan). Python stays below the
  primitive line: it manages no window.
- **M3's core.** `standard_io_window` draws: activate/show (border, label strip, rule), set_title
  (the label), clear, putl (wrap, scroll, key#lf), the echo of typed codes (none for the
  password), the block cursor of the selected window, kill. `pmacs_window`'s text protocol and
  `get_interpreter/2`, `has_been_reshaped/1` are not on the live route (they need the PIMOS
  console, M4).
- **M5's window part.** The Login PIMOS window, 40×7 cells of test_11, titled `Pimos remote
  login N` by the held requester, is pinned at three stages of the live run (after the node
  name; at the password, typed and not echoed; after the local login's replies), each by its
  text read back from the frame by glyph matching, the frame's PBM sha256 and dot count. PNGs at
  1,280×1,024 (`windev.png_bytes`, stdlib zlib) are written by `../../psi/winshot.py`; two are
  in `screens/`, the second from step 3n's bridged run (PIMOS's own replies, replayed from its
  tape; `test_win_m5_bridged_screen`). The status band is not drawn yet.

**Status (2026-11-25, window M4 and M6): PIMOS's console runs on the PSI, and the screen has its
chrome** (`../../psi/README.md` "Window M4 and M6"; tests `test_espc.py` `Window`
`test_win_m4_console`, `test_win_m6_system_menu`, `test_fep_bridge.py` `Console`):
- **M4, done, on real PIMOS.** `../../psi/fep_bridge.py` now routes PIMOS's 104 (create_window)
  devices to the PSI. A live run (PIMOS on pimm.py from the link checkpoint, 28 s) recorded
  `../../psi/fep_bridge_tapes/console_pwd.json`, which the tests replay. PIMOS's own messages
  are 104 → 127 (200, 200, 47, 14) → 130 `PIMOS CONSOLE` → 132 `font:test_11.font` → 143 → 70
  ×3 → 112 → 111 `Shell>> ` → 112 ×2 → 110. The HELD `pimfep##pimos_window_process`,
  `pimos_window` and `pimos_window_editor` run them on new stand-ins (`pmacs_window` rewritten,
  `editor_text_buffer`, `buffer_region`, `editor_command_interpreter`, `pmacs_request`; OURS
  bodies, INFERENCE/INTERPOLATED where their heads say). The user clicks in the console and
  types `pwd`. The 110's answer `{28, 1, "pwd"}` is the held editor's own (getl_from_buffer/3,
  run by carriage_return's after-demon), and PIMOS's reply ` The value of task: directory is
  ">sys>user>pmpsi" .` and the next `Shell>> ` are drawn under it. fep.py answers none of the
  window's messages (its log is empty). One opcode was added: `blt 69 not_equal_string`
  (KNOWN-PLAINTEXT, kappa2 KP_UPT.ESP:124/131), which set_font/4 needs. Screen:
  `screens/pimos_console.png`. The planned injection (drop 132's font) changes no dot,
  because 132 names test_11, the device's default font. So the test also checks the window's
  font object, and that check fails (J2). The nine observed injections are in
  `test_win_m4_console`'s header.
- **M6, partly done.** Drawn:
  - the status band (black, the frame's rows 944-1023): `USER : pmpsi`, `SIMPOS Version V7`;
  - the box naming the selected window as `<class>/<n>`;
  - the SYSTEM MENU, opened by `mouse#rr` at the mouse, two columns of login.com's 7 + 3 items,
    the item under the mouse boxed by an exclusive_or rectangle;
  - a left click on `Login PIMOS` closes the menu and starts the held requester, its window
    centred on the click;
  - selection by `mouse#l` (the console in the M4 run).

  The mouse events are `{mouse, Button, X, Y}` and `{move, X, Y}` on the coordinator's stream
  (OURS). The M4 tape's user script uses them (`fep_bridge.py`; the tape keeps it), and the
  login window lands at (755, 544). `test_win_m6_selection` shows that the keys follow the
  window selected by the mouse (injections J5 and J6 fail it). Not done: the date,
  `create`/`kill` by rubber band, `SWAPPED`/spool. Screens: `screens/system_menu.png`;
  `login_pimos_*.png` re-rendered with the band. The M5 frames with the band's rows cleared
  still equal M5's pins.

**Status (2026-11-25, window M6's rest and M7's save areas)** (`../../psi/README.md` "Window
M6's rest and M7's save areas"; tests `test_win_m7_save_areas`, `test_win_m6_date`,
`test_win_m6_create_kill`, `test_standin_refusals_loud`):
- **M7, partly done: the save areas.** A pop-up (the menu) and a window save the dots under
  them before they draw and restore them when they go (winfb `save`/`restore` through
  `windev.py` save/7, restore/3; the allocator `save_memory.esp`, OURS; PROSE TM-225 p10,
  TM-126 p5). Proved over the Login PIMOS window: the frame after menu open + close equals the
  frame before, closed four ways; out of save memory is a loud refusal. Not done: the
  manipulator (HIDE/SHOW, MOVE, RESHAPE, restacking) and output permission, so
  `test_win_m7_manip` as planned is still open.
- **M6, done but SWAPPED/spool.**
  - The date `20-May-93 Thursday 00:00:00` at the band's row 2 right (SCREENSHOT TM-153 p28,
    TM-115 p25, FSTJ p99). Its source is the PSI's `date_time`, day 33742 = `ref/pimm/fep.py`
    DATE, time 0: deterministic in every run and replay. Every band pin moved by -941 dots,
    accounted by masking the date.
  - create/kill: the second choice of a shown program opens a `create`/`kill` pop-up
    (SCREENSHOT simpos.wmv@49-60, prolog.wmv@14-15). `create` sweeps a rubber-band outline by
    two corner clicks (exclusive_or; TM-125 p8 RESHAPE). The new window takes the outline's
    top-left. `kill` exterminates the newest such process, and its window restores what it
    covered.
  - SWAPPED and spool: shown in TM-153 p28, FSTJ p99 and Giho 8609 p16, but no source read
    says what sets them, so they are not drawn (recorded in `status_band.esp`).
  - Screens: `screens/menu_over_window.png`, `create_kill_popup.png`, `rubber_band.png`.
- espc now refuses loud when a stand-in predicate is refused (nine known HELD-SOURCE
  refusals listed in `espc.KNOWN_STANDIN_REFUSALS`).

**Status (2026-11-25, window M7: the manipulator and keyboard focus)** (`../../psi/README.md`
"Window M7: the manipulator and keyboard focus"; tests `test_win_m7_manip`,
`test_win_m7_keyboard_focus`, `test_espc_swallowed_head`):
- **M7, done but the other permissions and items.**
  - The manipulator opens on the middle button over a window (OURS; TM-125 puts it on the system
    menu, which the held login.com lacks). Its items SHOW, HIDE, RESHAPE and MOVE are verbatim
    from TM-125 p8.
  - Restacking lifts the windows above top-down and lays them back bottom-up. Each pane's own
    dots and its under-area are kept in save areas (PROSE TM-225 p10, TM-126 p5). MOVE copies
    the dots across in the frame, since winfb's restore is bound to its place. MOVE and RESHAPE
    send reshape/5 and the held callback `has_been_reshaped/1`.
  - Pinned against frames built without the manipulator: HIDE then SHOW gives back the frame
    exactly (the planned pin); a kill under another window equals a run that never made it;
    MOVE equals a window made there.
  - Output to a covered window has permission `out` (TM-225 ②, the held `permission(out)`): the
    windows above are lifted while it draws. MOVE of PIMOS's console runs through the stand-in
    `has_been_reshaped/1` (`test_win_m7_console_move`).
  - Open: the permissions wait/show/notify; the other eight items; a Pmacs RESHAPE that changes
    the text size.
- **Keyboard focus.** Each window reads its own input stream, and keys go to the selected window
  (TM-225 p11). A selection brings its window to the top (INFERENCE, TM-225 p11).
- Screens: `screens/window_manipulator.png`, `manipulator_hide.png`, `manipulator_reshape.png`.

**Status (2026-11-26, window M7's rest: M7 done but three items)** (`../../psi/README.md` "Window
M7's rest"; tests `test_win_m7_permissions`, `test_win_m7_popup_over_writer`, `test_win_m7_items`,
`test_win_m7_has_been_selected`, and `test_win_m7_console_move` changed):
- **Output permission**, all four (PROSE TM-125 p5-6, TM-225 p10-11; Fig. 4's `out / wait / show /
  notify`): by the held `permission(P)` option, `set_permission/2`, or the manipulator's PERMISSION
  item. `wait` holds the writer's process back until the window is uncovered. `show` raises and
  selects the window. `notify` opens a temporary window at the mouse offering `wait` and `show`
  (its look is OURS). The default stays `out` (OURS; TM-225's default is ① wait).
- **A pop-up over a writing window**: the pop-up is lifted first and laid back last, so the output
  goes into its save area. A sweep's outline is taken off around the write.
- **The manipulator's items**, in TM-125 p8's order: EXPAND (OURS order of the edges), MENU (the
  windows by title, OURS), PERMISSION, EXIT are added. Not offered: ATTRIBUTE (a choice window, M9;
  added since, see the M9 status), HARDCOPY (no printer), SUPERIOR/INFERIOR (no window hierarchy).
- A writer held back is woken when its permission becomes `out` or `show`; a killed window's
  waiters are dropped (OURS) (`test_win_m7_permission_change`).
- **`has_been_selected/1`** is sent after a selection (the select notifier's callback; the
  stand-ins' primary does nothing, OURS).
- **Pmacs RESHAPE** sets the text size to the cells that fit (INFERENCE from the held
  `set_inside_size/5`), and the buffer is drawn again at that width.
- Screens: `screens/manipulator_expand.png`, `manipulator_menu.png`, `notify_window.png`;
  `window_manipulator.png` re-rendered (eight items).

**Status (2026-11-26, window M8, partial at merge 20efface: lines, rectangles, strings, transfers,
markers; the rest below)** (`../../psi/README.md` "Window M8"; tests `test_win_m8_graphics`,
`test_win_m8_forms`, `test_win_m8_markers`):
- `draw_line/5-8`, `draw_rectangle/5,7,8`, `draw_filled_rectangle/6,8` (pattern `fix`),
  `draw_string/4-6`, `transfer/8`, `execute_graphics_command/2` and `get_mouse_position/3` are
  stood in on `standard_io_window`. The held paragraph `type_switch_icon` `draw_box/5` draws
  through `execute_graphics_command/2` on them, and gives pinned frames. A slanted line drawn twice
  with the default exclusive_or erases itself. The held paragraph `g_window` `draw_list/8` (the
  mono list: five-element `draw_string` commands with a font) draws too.
- Markers (W§2.6, TM-125 p17's selectors): create, draw, erase, move, type `box`/`line`, size and
  list, on a stand-in class `marker`; drawn with exclusive_or, the look OURS.
- Only winfb's frozen primitives are used. No new primitive was needed, so the hardware contract
  (§4.1) is unchanged.
- Open: circles, arcs, ellipses, polygons, fill patterns other than `fix` (g_window's bar views
  refuse), `copy/9`, `paint/5`, images, `get_marker_position/4` (UNSPECIFIED). Each refuses loudly
  or is not stood in.
- Screen: `screens/window_graphics.png`.

**Status (2026-11-26, window M8's rest: done but for `paint/5`, a STOP)** (`../../psi/README.md`
"Window M8's rest"; tests `test_win_m8_patterns`, `test_win_m8_images`, `test_win_m8_shapes`,
`test_win_m8_copy`, `test_win_m8_rest_screen`):
- Fill patterns: the named ones (`light_paint` HELD-DERIVED from paragraph's saved images, the
  others' looks OURS) and the held pattern strings (64 x 64 tiles, INFERENCE), so g_window's
  bar views run. kl0 gained blt 44 `divide_with_remainder` for the held `set_pattern/2`.
- Images: `restore_image/6`, `get_label_height/2`, a `bitmap` stand-in (`get_plane_count/2` = 1);
  the held `type_switch_icon` `draw/6` runs through the held `restore/7`.
- Shapes: circles, ellipses, arcs, elliptical arcs, fans, the filled forms with patterns,
  graphs and polygons (TM-785 p40's vectors), their dots OURS and checked dot by dot.
- `copy/9` between two shown windows, with screen copy, save and restore only. The held caller's
  off-screen source (a 2000 x 2000 `hide_window`) and the scaled matrix form are refused.
- **STOP: `paint/5`.** A seed fill needs the frame's dots, and no frozen primitive gives a dot's
  value to the program, so it is refused loudly. `save_image/6` is not stood in for the same
  reason.
- The five refusals (paint, save_image, the off-screen `hide_window`, the matrix `copy/9`, TM-785
  p40's six-element ellipse) are researched in `m8_stops.md`. It gives the sources, what the PSI
  did, and a recommended resolution for each.
- Patterns and images are drawn as winfb's styled `line` (its style operand). No primitive was
  added, so the hardware contract (§4.1) is unchanged.
- Screen: `screens/window_graphics_rest.png`.

**Status (2026-11-26, window M9: choice windows)** (`../../psi/README.md` "Window M9"; tests
`test_win_m9_choice`, `test_win_m9_attribute`, `test_win_m9_choice_screen`):
- A `standard_choice_window` stand-in serves the HELD pimfep superviser's error mode menu
  (`create_error_mode_menu/1` on the .ptf, then `refute_sub_command/2`'s sends). Its fields are
  label lines, text fields (shown, not edited: OURS), choose and boolean fields, with the current
  value reversed (Fig. 4). It adds a do_it/abort row (INFERENCE). `read/2` gives
  `[{Key, Value}]` or `abort`. The look is OURS.
- The manipulator's ATTRIBUTE item opens a choice window with Fig. 4's PERMISSION field only
  (OURS subset); do_it sets the permission.
- The plan's injection (return the default for an edited field) at first failed nothing: the
  test's one edit ended on the held default. The test now edits away from it.
- Not done: the remaining menu kinds (W§2.9: `standard_temporary_menu`, the multiple-select and
  multi-column menus), editing a text field, and the other choice-window classes
  (`temporary_choice_window`, `..._with_no_execute`).
- Screens: `screens/choice_window.png`, `screens/manipulator_attribute.png`.

Also pinned (2026-11-26): the coordinator's own process is never held back (P13), by
`test_win_m7_coordinator_writes`.

The look, each choice cited or OURS, is in `window_pane.esp`'s head comment.

M0-M4 make the FEP route usable from a keyboard, about 1,200 lines. M5-M7 make it look like
SIMPOS, about 1,100. M8-M10 serve the IFS applications.

**Known decisions that are OURS** (to be labelled in the files and listed in a source check, as
step 3l did):
- the event format and the pump;
- the numeric `key#`/`mouse#` codes (G2);
- the status-band height;
- the substitute `font_13` and kanji box;
- the menu geometry: item height = font line height + 2;
- the save-area allocation (first fit) and the date's clock (fep.py's day, time 0);
- that the create/kill pop-up comes only for a program already shown;
- the manipulator on the middle button, the order of MOVE's copies, and type-ahead to the next
  selected window;
- EXPAND's order of the edges, MENU's titles, the notify window's look, and `out` as the default
  permission;
- Pmacs's default bindings.

---

## 6. Open questions and gaps that need inference

| id | question | best current answer | grade |
|---|---|---|---|
| Q1 | PSI-II physical resolution and status-band height | logical screen 1280×944 (TM-785; kl1graph); PSI-I product 1280×960 (Giho 8609) | INFERENCE |
| Q2 | numeric key and mouse codes (W gap G2) | choose locally, keep behind the `#` expander | OURS |
| Q3 | `font_13` and kanji glyphs | not held; substitutes in §1.4 | OURS |
| Q4 | the 32-bit `.font` family (kappa2 `tiny_7.font`, euod, fuzclust) | undecoded (W gap G9); compare with the held f822 `tiny_7` | — |
| Q5 | kana-kanji conversion | lost; the band layout is SCREENSHOT; a romaji-to-kana table is OURS if wanted | SCREENSHOT/OURS |
| Q6 | Pmacs default bindings (W gap G6) | Emacs-like (PROSE IPSJ 114007), so a small Emacs subset, labelled | INFERENCE |
| Q7 | does `nature([..])` at create mix at run time (W gap G29)? | stand-in: accept and record; behaviour from the listed mixins | INFERENCE |
| Q8 | what the status box shows: the selected window or the one under the mouse (W gap G14) | the selected window (TM-112 p9 PROSE for 1.0) | PROSE (1.0) |
| Q9 | window manager process structure; how `:x` gets `:do_x` run in the manager (TM-115 W3) | one manager process with a request stream; user methods put requests | INFERENCE |
| Q10 | the 56 UNSPECIFIED selectors (W§8) | fail loud until a caller is on a milestone's route | — |
| Q11 | how the display handler and the console processor reach the window manager (B4) | the stand-in handler process of §4.3 | INFERENCE |

---

## 7. Sources

### 7.1 This session's bounded search (2026-11-25)

**On disk, newly read for the window plan** (all are already held; nothing was downloaded, so no
manifest changes):
- `nonlocal/psdpim.tar.Z` → `psdpim/FONT.DIR/`: six f822 fonts and an 80×80 icon, decoded (§1.4).
  The archive is ICOT's and is in git.
- Mitsubishi Denki Giho 60(9) 1986, PDF p13 (folio 7 (599)): MELCOM PSI display 1,280×960 dots;
  Fig. 2, the I/O devices. Page image read.
- Mitsubishi Denki Giho 65(6) 1991:
  - PDF p86: the SIMPOS window system on PSI/UX as one X window, equivalent to the PSI-II
    screen; window control, mouse and keyboard handled by SIMPOS; full operating compatibility
    with PSI-II; the SIMPOS functions table (overlapping multiwindow, window manipulator, file
    manipulator by mouse);
  - PDF p88: Table 1 (Unix-side display 1,280×1,024, 256 colours) and the Fig. 1 photo.
  - Page images read.
- Giho 89-07 line "1,280×1,024" (text layer) is the ME engineering workstation, **not** a PSI.
  It is noted here so that nobody cites it as PSI-II.
- `cil/src/cil_kl0.esp` (held IFS) and `required/builtins.tsv`: no bitmap built-in (§1.5).

**Web** (WebSearch, four queries, 2026-11-25):
- PSI-II display resolution in Japanese (逐次型推論マシン, ビットマップディスプレイ, 解像度);
- SIMPOS window-system papers (SIMPOS ウィンドウシステム);
- MELCOM PSI keyboard and display specifications in English;
- ICOT PSI-II workstation display resolution in English.

The only relevant hit was IPSJ 36239, already held. A Giho 1989-03 issue
(`giho.mitsubishielectric.co.jp/giho/pdf/1989/8903.pdf`) was listed for the display query. It is
not held and was not fetched; whether it covers PSI-II is unknown. The earlier searches recorded in
`../psi_acquisition.md` §9-§16 cover the rest, and found no SIMPOS code anywhere.

### 7.2 Still worth searching or reading

| source | why | where | status |
|---|---|---|---|
| TR-265 (PSI-II hardware architecture) | PSI-II display, keyboard and console processor | `nonlocal/lit/trtm/` | held, page scans; **unread for display/keyboard** |
| Giho 8612, 8712, 8802, 8812 | tagged "PSI-II hardware" in `notes/ipsj.md` | `nonlocal/lit/journals/mitsubishi_giho/` | held; a text-layer grep (2026-11-25) found no PSI display resolution; page images not read |
| Giho 1989-03 (`8903.pdf`) | listed by the display query | Mitsubishi's Giho site | not held; fetch into a new empty directory, manifest only |
| TM-224 p11, TM-225 p8-15 | display, frame memory, window manager structure | held | partly read (`listings/TM-225_p08-11_window.txt`) |
| 「ESPプログラミング説明書－入出力管理編」 and 「SIMPOSプログラミング説明書(II) 入出力編」 (1987) | the I/O manual WINCS drew on; it would turn most INFERENCE in W§1-2 into PRINTED | no library found (`../psi_acquisition.md` §12) | lead |
| JAIST's preserved PSI and its "related manuals and materials" | a running SIMPOS screen, or media | institutional route (`../psi_acquisition.md` §15) | needs the owner; nobody contacted |
| The two archive.org lending-library proceedings (MFCS'86, ICLP'86) with SIMPOS screens | more screenshots | needs an account (`../psi_acquisition.md` §16) | not reachable |
| ICOT museum `Museum/VIDEO/` beyond the PSI segments | more screen footage | AIST archive mirror | not mirrored, by decision (`../nonlocal/LIT_MANIFEST.md`) |

---

## 8. Verification of this page

- The census figures in §2.1 were re-run on this tree at 167ea83d (2026-11-25):
  `python3 -I psi/kl0.py census --fep` and `--fep --recipes`.
- The font facts in §1.4 were measured on `psdpim/FONT.DIR` extracted from the tracked
  `nonlocal/psdpim.tar.Z`, with the recipe above.
- The Giho facts were read on page images rendered with `pdftoppm` at 150 dpi.
- This is a documentation change only. The ten `asm/*.py --check` passes were run before commit.

---

## 9. Hardware

`window_hardware_plan.md` (2026-11-25) is the plan for this environment as hardware: Bluespec RTL,
checked in Bluesim, then the ULX3S. In brief:
- **The device layer of §4.1 becomes RTL.** Its primitive set is the interface of a framebuffer
  box (`mkWinFbBox`), and the box is checked byte for byte against this layer's PBM output. A
  DVI scan-out and a keyboard/mouse box sit beside it.
- **The first CPU is kl0 on the host**, which sends drawing commands over the UART. The CPU route
  after that is the PIM/m PU itself, since the PSI-III and the PIM/m PE are one chip (TM-862): a
  KL0 front end on the Bluespec core in lockstep with `kl0.py`, then the held PSI-III microcode.
- **Display numbers, MEASURED in a scratch synthesis:**
  - native 1280×1024@60 does not close on the ECP5;
  - a 1,280×1,024 frame letterboxed 1:1 in 1920×1080@30 does;
  - the one-bit frame costs 80 of the 85F's 208 block RAMs.
- **Milestones H0-H13** mirror M0-M11.

The hardware plan reads this page's primitive set (§4.1) and event format (§4.3) as its contract,
so a change to either is a change to both.
