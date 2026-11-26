# Window M8's five refusals: what the sources say, and how to resolve them (2026-11-26)

Window M8's rest (merge f825683e) refused five forms loudly. This page gathers what the primary
sources say about each, what the PSI did where that is known, and a recommended resolution with
its grade. It is research only: no code changed. It extends `../../psi/README.md` "Window M8's
rest", `window_environment_plan.md` M8 status, `window_hardware_plan.md` §1-§2 and
`subsystems/window.md` §2.5.

Grades are the project's: PRINTED, PRINTED-INTERFACE, PROSE, USAGE (= HELD-SOURCE, a held
program's call), INFERENCE, OURS. "computed" is arithmetic on sourced or measured numbers.
"ESTIMATE" marks an RTL cost that has not been synthesized.

The held sources were read from the archives under `../nonlocal/ifs/` (icotext, kappa2, gog-esp,
cil, fuzclust, euod) and `../nonlocal/pimos.tar.Z` (paragraph). Each was extracted into a scratch
directory and decoded per ISO-2022-JP segment. Line numbers are the files' own.

---

## 0. Summary

| # | form | finding | recommendation | grade of the fix |
|---|---|---|---|---|
| 1 | `paint/5` | TM-785 p20 (PROSE, a drawing-tool menu item) describes the operation: fill **the closed region containing the point** with the pattern. That `paint/5` is this operation is INFERENCE. Connectivity is not printed. Held callers fill triangles bounded by 1-dot slanted lines, which only a 4-connected fill keeps inside | a span (scanline) seed fill, 4-connected, over the seed's region of equal value (every held seed is white inside black), the pattern anchored as `draw_filled_rectangle`'s. It needs dots read back (row 2) or a fill engine in the box | INFERENCE (rule), OURS (body) |
| 2 | `save_image/6` | `(W, String, X, Y, Width, Height)`. The caller allocates a 16-bit string of ceil(W/16) x H x planes words. `save_image` fills it, and the program then copies it and writes it out as an ESP class: **words read by the program**. Printed read-back exists since 1.0: TM-125 p17 `get_point_value/4` | one new primitive, **read a rectangle** (frame or bitmap memory → words). It also serves `get_point_value/4`, held `copy_to_string/11` and `paint/5` | the primitive OURS; the need PRINTED-INTERFACE + USAGE |
| 3 | off-screen `hide_window` | TM-225 p10: hidden windows' images live in save areas in the **display's own bitmap memory**, "several to several tens of times" the frame memory, and output to a hidden window **writes its save area**. TM-125 ch.4 (PROSE): `bare_window` "makes the object and allocates the bitmap area"; that this happens at create is INFERENCE. Three held callers draw on windows never activated | **drawing surfaces**: every primitive takes a target, the frame or an area of bitmap memory. Bitmap memory moves to SDRAM (H8); 2000x2000 = 250,000 words does not fit block RAM | the split PROSE; the operand OURS |
| 4 | matrix `copy/9` | the held vectors `{2,0,0,0,2,0}` and `{Min/Max,0,0,0,Min/Max,0}` (and the commented `{0.8,...}`, `{1.5,...}`) fit only a **row-major 2x3 affine map, source to destination**: x' = a·x + b·y + c, y' = d·x + e·y + f. Width and Height are the **source** extent. TM-785 p20 says the window system provides `magnify` and `expand`, and euod calls `expand/9` with factors 2,2. Only `{2,0,0,0,2,0}` is reachable in the held caller | stand in the axis-aligned case (b = d = 0), nearest dot, done above the primitive line by read-rectangle + `restore_image`-style writes, or as an integer-magnify mode in the blitter. Rotation and shear stay refused | INFERENCE (layout), OURS (sampling) |
| 5 | TM-785 p40 `{200, 0, 100, 1, dotted, set}` | the 600 dpi page image prints exactly six elements: not an OCR error. Every held call has the `{CX, CY, RX, RY, [Width,] Pattern, Op}` layout: icotext `/8` (6 sites + 2 forwarders), gog `/6` (2 sites). None of the 18 SIMPOS archives, cil, paragraph or the 5 CESP archives has a `/7`. So the printed vector is **one element short**, and which element is lost cannot be recovered | keep refusing the six-element vector. **Add the held `/8` and `/6`**, which the stand-in lacks; its `/7` rests only on the defective vector | USAGE (the two held forms); the refusal OURS |

**The single most useful extension is drawing surfaces plus read-rectangle** (rows 2-3). Together
they unlock items 1, 2, 3, 4 (axis-aligned) and the held `get_point_value/4`, `set_point_value/4`,
`copy_to_string/11` and `copy_from_string/11`, none of which is stood in today. Both fit the
documented PSI split, in which the display device holds bitmap memory and draws into it. A seed-fill
engine inside the box serves only `paint/5`.

---

## 1. Context: the frozen primitive set is OURS

- The primitive set `fb_fill`, `fb_line`, `fb_glyph`, `fb_copy`, `fb_save`/`fb_restore` is **OURS**
  (`window_environment_plan.md` §4.1: "The primitives, each one OURS"; `window_hardware_plan.md`
  §1.2: every row of the RTL table is graded OURS). It was "frozen" so that `psi/winfb.py` and
  `bsv/WinFbBox.bsv` can be compared byte for byte (§1.2 "The interface is the contract"). That
  freeze is a verification discipline, not a source fact. Extending the set means changing both
  sides and their lockstep bench together.
- What is sourced about the PSI's display (`window_hardware_plan.md` §1.1):
  - The bitmap display was a Multibus device (TM-153 PDF p23, PRINTED figure).
  - Only the window manager touched bitmap memory in 1.0 (TM-115 p43, PROSE).
  - Frame memory is shown. Hidden windows are kept in save areas in the display's bitmap memory,
    "several to several tens of times" the frame memory. Restacking copies between them
    (TM-225 p10, PROSE TRANSLATION; `subsystems/listings/TM-225_p08-11_window.txt:28-32`).
  - No KL0 instruction draws. The rasterop was in the display controller or in microcode
    (INFERENCE, `window_environment_plan.md` §1.5).
- **New this page, from the same TM-225 passage (lines 28-32):** "Output to a hidden window writes
  the save area." So the PSI's drawing engine drew **into bitmap memory outside the frame**, not
  only into the frame (PROSE). The frozen winfb draws only into the frame; its save and restore
  move dots unseen.
- TM-115 (`subsystems/notes/tm115.md` W4, PROSE) describes 1.0 **bitmap areas**: off-screen
  bitmaps that are allocated, loaded from double-byte strings, transferred to a window and freed.
  Their widths are multiples of 16, and they are not cleared on allocation (p44, p79, p82).
- TM-125 (`subsystems/notes/trtm_window.md` W5; PDF p17, printed "Page 16", read here) prints
  `:get_point_value(Window, X, Y, ^Value)` and `:set_point_value(...)`, "read/write the value
  (0/1) of the pixel". Reading a dot back is part of the **1985 user interface** (PRINTED-INTERFACE).
- TM-125's class catalogue (ch.4, PDF p8-13; `subsystems/notes/trtm_window.md` W1) says the
  mixin `bare_window` "makes the object and allocates the bitmap area" (PROSE). Its method list
  (ch.5) has `deactivate/1`, which keeps the image, and `kill/1`, which releases the bitmap area
  (`subsystems/window.md` `kill/1` row; trtm_window W5). INFERENCE: a window has a bitmap area
  from `create`, before `activate`, because the mixin that makes the object allocates it.
- No document held describes the display controller's commands, a rasterop microcode routine, or
  the bitmap memory's size in words. `../psi_microword.md` and `../psi_acquisition.md` have no
  display or rasterop entry; the PSI-III's I/O bus is outside the PU (thesis p.130, via
  `window_hardware_plan.md` §1.3).
- **`bmm_size` cannot be turned into a size.** `:get_parameter(#ipl, bmm_size, Code)` gives
  16#07FF for monochrome. The PSI/UX patch maps 1 plane → 07FF, 3-4 → 0FFF, 6 → 17FF and
  8 → 1FFF (`subsystems/window.md` §2.13, USAGE paragraph `p_MAIN.esp:183-185`,
  `p_ux_patch.esp`). Read as (size − 1) in some unit, 8 planes would have only 4 times the mono
  memory, so the code is not proportional to the planes. Its unit is not printed (INFERENCE: a
  board-size code).

So extending the set is **consistent with the documented PSI split**, as long as the extension
stays a device-side operation on bitmap memory and no window logic moves below the line:
- drawing into a bitmap-memory area: PROSE TM-225 p10;
- reading dots back: PRINTED-INTERFACE TM-125 p17;
- loading areas from strings: PROSE TM-115 p82.

Whether a seed fill or a scaled copy ran in the controller, in microcode or in ESP is not
documented either way.

---

## 2. Item 3 first: off-screen windows (it gates items 1 and 2)

**The held callers.** All three draw on a window that is never on the screen:
- **icotext** `src/util_scroll.esp`:
  - class `as_scroll_window2`, line 57 (and `as_scroll_window`, :258) has the component
    `(hide_window := Win :- :create(#scroll_win, [size(2000,2000)], Win))`, where
    `scroll_win` = `as_graphics, inferior_window` (:49-52). It is never activated.
  - Every drawing method is forwarded to `W!hide_window` (:87-152): `get_point_value`,
    `set_point_value`, lines, rectangles, circles, ellipses, `draw_filled_ellipse/8`, fans, arcs,
    strings, `transfer/8`, `copy/9`, `copy_to_string/11`, `copy_from_string/11` and
    `execute_graphics_command/2`.
  - Then a `copy/9` from `hide_window` at (posX, posY) to the shown window at (0, 0) presents the
    view (`no_condition_copy`, :205-211). The window scrolls over the 2000x2000 canvas by moving
    (posX, posY) (`warp_screen`, `scroll_*`, :172-193).
- **kappa2** `user_if/pb/pdim.esp:579-617`: an icon window (61x64) is created, then
  `:paint(OPicon1, 1, 1, Pattern1, set)` (:606) and `write_line`, and only then `:activate`
  (:617). The same holds for the other ten painted icons (:650-1063; the eleventh, :982, is commented out).
- **paragraph** `pimos/src_util/paragraph/p_imag.esp`, `go1`-`go6` (:165-425): the window is
  created, `%:activate(Win)` is **commented out** (:174, :213, :248, :296, :352, :390), the icon
  is drawn, then `save_image` reads it (item 2).

The stand-in refuses all three: "drawing on a window not on the screen" is a loud refusal
(`../../psi/README.md` Window M8), and `copy/9` refuses a source that is not shown.

**What the PSI did** (PROSE, §1): an inactive or hidden window's image is its save area in the
display's bitmap memory, and output to it writes there (TM-225 p10, the OUTPUT permission ②). The
2000x2000 `hide_window` is 4,000,000 dots = **250,000 16-bit words = 500 KB** (computed). A
1280x1024 frame is 81,920 words, so the canvas is about 3 frames. That is within TM-225's
"several to several tens of times".

**Recommendation: drawing surfaces** (OURS operand, PROSE basis):
1. Each primitive (`fill`, `line`, `glyph`, `copy`, styled `line`) gets a target operand: the
   frame, or a surface = (base, pitch, width, height) in bitmap memory. `save`/`restore` become
   copies between surfaces, as TM-225's restacking is.
2. The stand-in gives a window a surface when it first needs one while not shown (OURS: lazy,
   where TM-125's `bare_window` allocates at creation, an INFERENCE from ch.4's PROSE). A window
   that is created and shown at once needs none until it is covered. Lazy allocation keeps block
   RAM usable before H8. One full-screen 1280x944 window is 75,520 words, more than today's 65,536
   (computed), so eager allocation would need H8 first. A window not shown draws into its surface. Showing it copies the surface to the frame.
   This is the save area the M7 stand-in already keeps for covered windows, now kept for
   never-shown windows too.
3. `copy/9` takes any two surfaces.

**Cost.**

| quantity | value | grade |
|---|---|---|
| today's bitmap memory | 65,536 x 16 = 64 DP16KD; the box uses 156 of 208 | MEASURED (`window_hardware_plan.md` §5.1, yosys counts) |
| one 2000x2000 surface | 250,000 words ≈ 245 DP16KD at 1,024x16, more than the whole 85F | computed |
| bitmap memory in SDRAM, the plan's 8 MB partition | 4,194,304 words = 16 surfaces of 2000x2000, or 51 frames of 1280x1024: TM-225's upper bound | computed (§2.3's partition, OURS) |
| SDRAM path | `Sdram_Controller.bsv`: 256-bit (16-word) requests, two BL8 bursts at 25 MHz | repo (§2.3) |

- The RMW stage already chooses frame or bitmap RAM per command (`WinFbBox.bsv` `bDstSave`,
  rules `rReadSave`/`wSave`, :532-557), with a base and a pitch. Only the blit sets it; the line
  command's start sets it False, so a line always draws on the frame (:753, `mode <= MLine`). Targeting a surface means address generation by (base, pitch)
  in the line and glyph paths too. ESTIMATE: a few hundred LUT4 while bitmap memory stays in
  block RAM.
- The real cost is **H8**, bitmap memory behind the SDRAM controller: a line buffer or small
  write-back cache of 16-word lines (1-2 DP16KD) and an arbiter shared with any PIM/m core.
  ESTIMATE: 500-1,500 LUT4; the plan's H8 row says about 500 lines of BSV.
- The Python side (`winfb.py`) grows its `save` array to the same size. The surface table replaces
  the 16-slot save table, and the lockstep bench compares both memories.

Until H8, a 2000x2000 surface is refused as **out of bitmap memory** (winfb BADSAVE), not as "not
shown". That is the PSI's own failure mode.

---

## 3. Item 2: `save_image/6`

**Signature** (USAGE, paragraph):
- `:save_image(Win, String, X, Y, Width, Height)`: `p_imag.esp:198, :234, :282, :338, :376,
  :420`; `p_v_imag.esp:228, :238`.
- The caller allocates the string first: `new_string(St1, H0*NB1, 16)` (`p_imag.esp:197`), where
  NB1 = `get_plane_count(#bitmap)` (`color_check2`, :608-616), or
  `new_string(GString, (384/16)*238*Col, 16)` (`p_v_imag.esp:227`). So it is **ceil(Width/16)
  words a row x Height x planes**, 16-bit elements. Width is passed as a multiple of 16 (16, 64,
  112, `(384/16)*16`). The 112-wide and 64-wide reads allocate `H0*7*NB1` and `H0*4*NB1` words (:337, :375), which confirms ceil(Width/16) words a row.
- `save_image` fills the string. It is the inverse of `restore_image/6`, which is stood in, MSB
  leftmost (TM-115 p74-76).

**What the program does with it** (USAGE):
- `set_substring(St, 0, H0, St1)` copies the first plane into another string (`p_imag.esp:199`,
  `p_v_imag.esp:240`).
- The string is written as source text by `:write(_, S, F, Name)` (:38-50): a class whose `:get`
  returns the string, through `make_image_class_file` / `make_icon` (:54-80). `make/3` (:111-129) runs `go1`-`go6` and
  writes each string with `:write`, so the strings from `save_image` become those class files.
- **This is how the held `profiler_*_image` classes were made.** The light_paint derivation in M8's
  rest read those saved images.
- So the result is **words the program reads and keeps**, not a bitmap object.

**Neighbours that also read dots back** (USAGE):
- fuzclust `src/hikaku.comp:148, :154` branches on `:get_point_value(Window, SX, SY, Value)`.
- icotext forwards `get_point_value` and `copy_to_string(Wdw, S, W1, H1, X1, Y1, X2, Y2, W2, H2,
  Ope)` to its canvas (`util_scroll.esp:87-88, :145-147`). The 11-argument layout's field
  meanings are not printed (INFERENCE: a string of W1 x H1 and two rectangles).

**Recommendation:** one primitive, **`read surface x y w h`**, answered as ceil(w/16) x h words
(OURS):
- The dump engine already streams the frame's words as `isData` responses (`WinFbBox.bsv`
  header). A rectangle read from frame or bitmap memory is that engine with a rectangle and a
  shift. ESTIMATE: 200-500 LUT4, no new block RAM.
- In option (a), with the CPU on the host, the words cross the link. A 16x56 icon is 56 words =
  112 bytes, about 1 ms at 1 Mbaud. A 384x238 view is 5,712 words, about 0.11 s. A whole 2000x2000
  canvas is 500 KB, 5 s (computed from §3.4's 100,000 B/s). The plan's rule "primitives, never
  pixels" (§3.4) then holds for drawing but not for reads; reads are rare.
- Stand-in bodies (OURS) on top of it:
  - `save_image/6`: the read words written into the caller's string;
  - `get_point_value/4`: a 1x1 read, the bit;
  - `set_point_value/4`: a 1x1 fill with `set` or `reset`;
  - `copy_to_string/11` and `copy_from_string/11`, once their fields are settled. They are not
    needed by any route program.
- With more than one plane (`get_plane_count` > 1) the string holds planes in turn
  (INFERENCE from `H0*NB1`). The stand-in screen has 1 plane.

---

## 4. Item 1: `paint/5`

**Signature** (USAGE): `:paint(W, X, Y, Pattern, Op)`.
- kappa2 `pdim.esp:606` and ten more live sites, plus one commented out (:982). Its patterns come from `get_paint_pattern/2`
  (:1081-1101), which cycles through `right_hatch`, `left_hatch`, `small_mesh`, **`rough_dotted`**
  and `dotted`, and falls back to `fix`. `rough_dotted` is a pattern name the stand-in lacks
  (`window.md` §2.5 does not list it); kappa2 `IVTMNG.ESP:1865` (commented) uses it too.
- gog-esp `DISPPBMS.esp:117-118`.
- cil `src/es_gin.esp:1761-1762, :1824`.

**Meaning, PROSE (TRANSLATION).** TM-785 PDF p20 (folio 15, read on the page image): 閉領域塗り潰し "fills
the closed region that contains the clicked point with the fill pattern chosen in the
drawing-attribute window". A left double click lets the user clip the fill to a given rectangle.
This is the PSI drawing tool's menu item (Fig. 2-13, p19), not a method page. That `paint/5` is the method behind it is INFERENCE (the name and the one-dot seed). It gives the meaning,
a fill of the **closed region containing the seed**, but not the connectivity rule.

**What the callers constrain** (INFERENCE):
- gog `DISPPBMS.esp:115-118` draws "▲" as `:draw_polygon(W, [(X+10,Y+1),(X+2,Y+15),(X+18,Y+15),
  (X+10,Y+1)])`, then `:paint(W, X+10, Y+10, fix, set)`. "△" is the same polygon without the
  paint. The edges have slopes 14/8, so a 1-dot line steps diagonally between rows. **An
  8-connected fill leaks out through every diagonal step**; a 4-connected fill stays inside. The
  caller expects a filled triangle, so the rule is 4-connected. This is unless SIMPOS drew
  4-connected lines, which no source says.
- cil `es_gin.esp:1752-1762` `draw_triangle/3` draws an arrowhead from three 1-dot lines: two
  45-degree diagonals from (X, Y) to (X+5, Y∓5), and the vertical at X+5. It then paints from two
  seeds, (X+3, Y+2) and (X+3, Y−2). A 45-degree 1-dot line is a pure diagonal staircase, so an
  8-connected fill leaks through it at every dot; a 4-connected one does not. The interior is one
  4-connected region (through row Y), so the second seed is redundant under either rule
  (INFERENCE: a defensive call). The horizontal line along row Y (:1745) is drawn *after*
  `draw_triangle` (:1743), so it does not split the region at paint time.
- cil `draw_vector_node` (:1810-1824) is a triangle of 1-dot slanted lines, painted from its
  centre: the same argument as gog's.
- Every held seed is a white dot inside set (black) lines. "Fill up to the set dots" and "fill the
  seed's 4-connected region of equal value" agree on all of them. What paint does from a black
  seed is not exercised by any caller. The stand-in should take the region of the seed's value
  (OURS) and say so.
- kappa2 paints a **blank** 61x64 icon window at (1, 1): the region is the whole inside, clipped to
  the window. Paint never leaves the window's inside (INFERENCE, as every other drawing).

**Pattern and op** (OURS, consistent with the stand-in's `draw_filled_rectangle/8`): the region's
dots are drawn with the pattern tile anchored at the inside's top-left, through Op. The region is
found on the dots **before** drawing, so `exclusive_or` or a sparse pattern does not change it.

**Recommendation:**
- **(a) Above the line (first):** the stand-in reads the window's inside with `read` (§3) and runs
  a span seed fill in ESP (OURS body, 4-connected). It then draws each span as a styled `line` or
  a `fill` through the pattern, which M8 already does for patterns. Cost: no RTL beyond `read`. A
  61x64 icon is 256 words read and at most 64 spans. kl0 runs a few thousand list steps, which is
  acceptable for the route programs.
- **(b) In the box (optional, later):** a `paint surface x y pattern op` primitive. A scanline
  fill needs a span stack. Its worst case on a 1280x1024 frame is bounded by about the height
  times the spans a row; 1-2 DP16KD hold 1-2K (x, y) entries. Each span is a read of the row's
  words plus a pattern fill through the existing RMW stage. ESTIMATE: 1,500-3,000 LUT4 and 1-2
  DP16KD. It serves only `paint/5`, and a stack overflow must refuse loudly. (b) is consistent
  with the PSI split too, since where paint ran is undocumented. It is worth doing only if (a) is
  too slow on a real caller.

---

## 5. Item 4: the matrix form of `copy/9`

**The held caller** (USAGE, icotext `util_scroll.esp`, class `as_scroll_window2`):
- `no_condition_copy/1` (:205-226) and `no_condition_copy2/1` (:232-253) call
  `:copy(W, 0, 0, W!hide_window, W!posX, W!posY, IntX, IntY, {Min/Max,0,0,0,Min/Max,0})` (:220-221,
  :247-248). IntX = (SizeX − min_pos_x)·Max/Min, so the source extent scaled by Min/Max is the
  window's inside.
- They also call `:copy(W, 0, 0, W!hide_window, W!posX, W!posY, SizeX/2, SizeY/2,
  {2,0,0,0,2,0})` (:223-224, :250-251), where a half-size source scaled by 2 fills SizeX x SizeY.
- Commented out (:227-231): `{0.8,0,0,0,0.8,0}` and `{1.5,0,0,0,1.5,0}`, both with SizeX, SizeY.
- Argument order: `(Dst, DX, DY, Src, SX, SY, Width, Height, Matrix)`, where the plain form is
  `(Dst, Src, SX, SY, DX, DY, Width, Height, Op)` (:211).

**What the matrix holds** (INFERENCE, discriminated by the held vectors):
- The elements are numbers, floating point in the `Min/Max` case: scale factors, not a bit matrix.
- In every held vector the non-zero elements are 0 and 4 and are equal. Only a **row-major 2x3
  affine matrix** `{a, b, c, d, e, f}` puts the x and y scales there: x' = a·x + b·y + c,
  y' = d·x + e·y + f.
  - Read as 2x2 + translation `{a,b,c,d, tx,ty}`, `{2,0,0,0,2,0}` would scale y by 0.
  - Read column-major, d (element 3) would be the y scale, and it is 0.
- Width and Height are the **source** extent, and the map runs source → destination, about each
  area's top-left. That follows from IntX = extent/(Min/Max) and SizeX/2 x 2 = SizeX.
- b, d (shear or rotation) and c, f (offset) are 0 in every held call. Their meaning is the
  layout's, unconfirmed.

**Which calls are live** (USAGE, read in the code):
- `drawMode` is `normal` or `double` (`imi_draw_win.esp:46-49`; set by `imi_menu.esp:100-113`).
- In `normal` mode the plain copy at :211 has no guard (`%SizeX >= MaxPos, ...` is commented out).
  The `Min/Max` branch therefore runs only if that copy fails. In `no_condition_copy2` a cut
  follows (:238), so the branch is dead there.
- In `double` mode `{2,0,0,0,2,0}` runs when the window is at least `nodeMaxPos` in both sizes.
- So **the one reachable matrix is a x2 magnification**.

**Other sources:**
- TM-785 PDF p20 (folio 15, page image): the drawing tool's 拡大・縮小 offers "magnify and expand,
  provided by the window system" (ウインドウ・システムで提供しているmagnify とexpand), default
  expand (PROSE). 回転 (rotate) rotates a rectangle by a mouse-given angle, anticlockwise (PROSE).
  The method used for rotation is not printed.
- euod `DEF/def.esp:909`: `:expand(W, 0, 0, 0, 0, 640, 472, 2, 2)` before a hardcopy (USAGE,
  INFERENCE: (SX, SY, DX, DY, Width, Height, FX, FY) with integer factors).
- So the window system had scaled transfers of its own. `magnify/?` and `expand/9` are not in
  `window.md` §2.5 yet.

**Recommendation:**
1. Stand in the **axis-aligned** matrix (b = d = 0, c = f = 0 relative to the two corners) by
   nearest dot (OURS sampling). Each destination dot (x', y') takes source dot
   (floor(x'/a), floor(y'/e)). Done above the line, it is `read` of the source rectangle (§3), a
   resample in ESP, then a `restore_image`-style opaque write through Op (`copy` here). This needs
   no new RTL beyond `read`.
2. Optionally an **integer magnify mode** in the blitter: each source bit replicated k times, each
   row k times. It is cheap (ESTIMATE 300-600 LUT4: a bit-spreading table in the funnel). It also
   serves `expand/9` with integer factors.
3. Keep refusing a non-zero b or d (rotation, shear) and non-integer factors in RTL. General affine
   resampling needs per-dot random source reads and fixed-point multiply-accumulate (MULT18X18D).
   No held caller reaches it.
4. Grade: layout INFERENCE, sampling OURS. `expand/9` and `magnify` are named in PROSE and USAGE,
   but their bodies are unknown.

---

## 6. Item 5: TM-785 p40's six-element `draw_filled_ellipse` vector

**The page** (TM-785 PDF p40, folio 35): read here at 300 dpi and the line again at 600 dpi.
- It prints `data(draw__filled__ellipse, {200, 0, 100, 1, dotted, set}) ;`.
- There are six elements and the separators are clean. The `0` is a single character with
  ordinary spacing on both sides. **The transcription (`printed/listings/TM-785_p40.esp`) is
  right. There is no OCR reading that restores a seventh element.**

**The neighbouring layouts** (PRINTED):
- On the same page:
  - `draw_filled_rectangle {100, 50, 300, 200, 1, mesh, 5}` = X, Y, W, H, 1, Pattern, Op;
  - `draw_filled_circle {200, 200, 100, 1, left_hatch, set}` = CX, CY, R, 1, Pattern, Op;
  - `draw_ellipse {300, 300, 150, 100, 1, solid, 5}` = CX, CY, RX, RY, Width, Style, Op;
  - `draw_filled_fan {300, 300, 150, 95, 170, 1, small_mesh, 3}`.
- So the family is {geometry, a `1`, Pattern, Op}. Its ellipse geometry is CX, CY, RX, RY, which
  makes seven elements.
- WINCS PDF p3 (folio 56, page image) prints `:draw_circle(#my_window, X1, Y1, R, 1, solid, set)`,
  the same {geometry, width, style, op} layout. It has no filled form.
- The generator does not fix the arity. TM-785 PDF p35 (folio 30, page image) has
  `modify(draw_filled_ellipse, ...)`, which copies whatever length the vector has
  (`stack_vector(Args, Length)`, `copy_element(Length-1, ...)`). `refute/3` (p32) then sends a
  method of that arity.

**Every held caller** (USAGE; a full count over the 18 SIMPOS archives, cil, paragraph and the 5 CESP archives, extracted):

| form | sites |
|---|---|
| `/8` `(W, CX, CY, RX, RY, 0, fix, set\|reset)` | icotext `imi_draw_win.esp:252, :254, :266, :268, :281, :283` |
| `/8` forwarded `(W, X, Y, RX, RY, L, T, O)` | icotext `util_scroll.esp:116-117, :315-316` |
| `/6` `(W, X, Y, Rx, Ry, Op)` | gog-esp `CGS_DEMO.ESP:416, :424` (to `Obj!io_window`, a `standard_io_window`, :488-495); :182 sends to the demo object's own `/6` (:413), which forwards there |
| `/7` | **none** |

So the printed vector is **one element short** of the held `/8` layout `{CX, CY, RX, RY, 1,
dotted, set}`. Whether RX, RY or the `1` was lost cannot be recovered from any source held. With 0
as CY the shape is half above the window, so 0 is probably a corrupted value as well (INFERENCE).

**Recommendation:**
- Keep the loud refusal of the six-element vector (OURS). It now has a reason that is not
  "ambiguous": no held method takes that arity.
- **Add the two held forms to the stand-in.** `draw_filled_ellipse/8` `(W, CX, CY, RX, RY, _,
  Pattern, Op)`, like the filled circle's `/7`, and `/6` `(W, CX, CY, RX, RY, Op)`, pattern `fix`,
  like `draw_filled_circle/5`. Grade USAGE. In `execute_graphics_command/2` the seven-element
  vector maps to `/8`.
- The present `/7` `(W, CX, CY, RX, RY, Pattern, Op)` rests only on the defective vector. Relabel
  it INFERENCE or drop it. No held caller depends on it.

---

## 7. Order of work (recommendation)

1. **Small, no RTL:** `draw_filled_ellipse/8` and `/6`, the `rough_dotted` pattern (its look OURS).
2. **`read` primitive** in `winfb.py` and `WinFbBox.bsv` together, in lockstep. Then the stand-in
   bodies `get_point_value/4`, `set_point_value/4`, `save_image/6` (paragraph `go1`-`go6` and the
   `p_v_imag` save path become runnable once item 3 lands), and `paint/5` by (a).
3. **Drawing surfaces** (target operand), lazily allocated, with bitmap memory in block RAM first:
   kappa2's 61x64 icons (256 words each) and paragraph's 500x400 window (12,800 words) fit in it. Then H8 moves bitmap
   memory to SDRAM, which icotext's 2000x2000 canvas needs.
4. Axis-aligned matrix `copy/9` above the line. The blitter magnify mode is optional.

Each step changes the hardware contract, so each updates `window_hardware_plan.md` §1.2 and §2.4
and the winfb/RTL lockstep bench, and records the change as OURS.

**Status (2026-11-26, implementation):** the owner said "do it"; progress is recorded step by step
in `../../psi/README.md` "Window M8's stops resolved".
- Step 1 DONE: `/8`, `/6` and `rough_dotted` stood in (`test_win_m8_stops_ellipse`).
- Step 2 DONE:
  - the read primitive in `psi/winfb.py` and `bsv/WinFbBox.bsv`, in lockstep (`run_win_tb.sh`);
  - on top of it `save_image/6`, `get_point_value/4`, `set_point_value/4`, and `paint/5` as a
    4-connected seed fill (`test_win_m8_stops_read`).
  - The held paragraph run waits for step 3: it draws into windows that are never shown.
- Step 3a DONE: drawing targets (prim `b`) in the winfb contract, in `psi/winfb.py` and
  `bsv/WinFbBox.bsv` in lockstep, with bitmap memory 0 at reset (`window_hardware_plan.md` §2.4).
  The stand-in's use of them (hidden windows drawn in areas) is step 3b.
- Step 3b DONE (`test_win_m8_stops_surface`):
  - windows drawn before they are shown, or never shown, draw into surface panes in bitmap
    memory;
  - paragraph `make/3` runs go1-go6, but its images do NOT match the held ones (every word
    differs: line geometry and pattern phase, OURS; open in `psi/README.md`);
  - icotext's 2000 x 2000 canvas refuses loudly (H8).

## 8. Sources read for this page

- TM-785 PDF p19-20 (folios 14-15), p35 (folio 30), p40 (folio 35): page images.
- TM-125 PDF p17 (printed "Page 16"): page image.
- WINCS (Computer Software 8(1), 1991) PDF p3 (folio 56): page image.
- TM-225 p10, through `subsystems/listings/TM-225_p08-11_window.txt`.
- TM-115, through `subsystems/notes/tm115.md` W3-W4.
- Held source:
  - icotext `src/util_scroll.esp`, `src/imi_draw_win.esp`, `src/imi_menu.esp`;
  - kappa2 `user_if/pb/pdim.esp`;
  - gog-esp `DISPPBMS.esp`, `CGS_DEMO.ESP`;
  - cil `src/es_gin.esp`;
  - fuzclust `src/hikaku.comp`;
  - euod `DEF/def.esp`;
  - paragraph `p_imag.esp`, `p_v_imag.esp`.
- Repo: `../../psi/standin/standard_io_window.esp` (the refusals), `save_memory.esp`;
  `../../psi/winfb.py`; `../../bsv/WinFbBox.bsv`; `window_hardware_plan.md` §1-§2, §3.4, §5.1.
