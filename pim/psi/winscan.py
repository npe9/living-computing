#!/usr/bin/env python3
"""The scan-out model: video modes, the timing model, the displayed view
(frame + border + hardware cursor), and the checker of the Bluesim
scan-out bench.  The Python reference of bsv/WinScanOut.bsv
(mkWinScanOut), docs/simpos/window_hardware_plan.md H2.

EVERYTHING HERE IS OURS SCAFFOLDING (as psi/winfb.py): the PSI's CRT
controller is not documented (plan §1.1, §1.2).  What is sourced:
  - the TMDS characters, psi/wintmds.py (DVI 1.0, its header);
  - the mode timings, below, each with its grade;
  - the frame's bit order and 1 = black, psi/winfb.py.

THE MODES (plan §2.2; one table, chosen at start).  Timings of modes 0,
1, 3 are SECONDARY: the Linux kernel's drivers/gpu/drm/drm_edid.c
(fetched 2026-11-25), which transcribes them as (hdisplay, hsync_start,
hsync_end, htotal; vdisplay, vsync_start, vsync_end, vtotal; flags):
  0  1920x1080@30, CEA-861 VIC 34 ("34 - 1920x1080@30Hz 16:9"):
     74.25 MHz, 1920 2008 2052 2200; 1080 1084 1089 1125; +H +V.
     The 1280x1024 frame letterboxed 1:1 at (320, 28) (plan §2.2, OURS).
  1  1280x1024@60, VESA DMT ID 0x23 ("0x23 - 1280x1024@60Hz"): 108 MHz,
     1280 1328 1440 1688; 1024 1025 1028 1066; +H +V.  Out of reach of
     the ECP5 PLL (plan §2.2, MEASURED there); kept for the table.
  2  1280x1024 reduced blanking, OURS (the plan's htotal 1440, vtotal
     1054 at 75 MHz, 49.4 Hz; porches from its Appendix A skeleton:
     48/32/80, 3/7/20).  Polarity +H -V, as CVT reduced blanking uses
     (CHECK: from memory, not sourced this session).
  3  640x480@60, VESA DMT ID 0x04 / CEA-861 VIC 1: 25.175 MHz,
     640 656 752 800; 480 490 492 525; -H -V.  The frame shown with the
     2:1 reduction (plan §2.2, OURS): each display pixel is the OR of a
     2x2 block of frame dots, so one-dot lines stay visible.  2:1 gives
     640 x 512 of the 1,024 rows, more than 480 lines, so the view
     starts at frame row panY (OURS register, default 0: rows 0..959,
     the MELCOM PSI's 1,280 x 960, PROSE, plan §2.1; panY = 24 shows
     the logical frame's rows 24..983, status band included).
Conventions (OURS): a line is active pixels first, then front porch,
sync, back porch; a frame is the active lines first; vsync changes at
the start of a line (hx = 0), as the plan's Appendix A skeleton does
(CHECK: CEA-861 aligns the vsync edge with an hsync edge for
progressive formats; no monitor test yet).  The frame start is the
first active pixel of the first active line.

THE VIEW (OURS).  The display window is fw x fh display pixels at
(x0, y0) in the active area.  Display pixel (u, v) shows frame dot
(u + 16 panX, v + panY) (1:1) or the OR of dots (2u + 16 panX + i,
2v + panY + j), i, j in {0, 1} (2:1).  Dots outside the 1,280 x 1,024
frame read as 0.  An active pixel outside the window is the border
level 0x20 (dark grey, OURS, so a slipped window shows); in the window
a black dot is 0x00, a white one 0xff, on all three channels.

THE CURSOR (plan §2.6, OURS): 8 shapes of 16 x 16 (mask, image) bit
planes, MSB leftmost; on/x/y/shape registers in display-window pixels
(the cursor is not scaled in the 2:1 mode).  x and y are 12- and 11-bit
registers and the cover test is modular (u - x mod 4096 < 16, v - y mod
2048 < 16), so x = 4095 or y = 2047 puts the shape one pixel off the
left or top edge, partly shown.  Where the cursor covers a
window pixel and its mask bit is 1, the pixel is black if the image bit
is 1, white if 0; elsewhere the frame shows.  Not drawn on the border.
The registers written by the system side take effect at the next frame
start.  The cursor is never written into the frame (the scan-out has
only a read port), so the PBM dump is the frame without it.

THE BENCH FILES (bsv/WinScanOutTb.bsv):
  win_scan.hex  160 words of 32 bits ($readmemh), written by `config`:
     0 mode (0-3, or 15 = custom, then 1-13 used)
     1 ha 2 hf 3 hs 4 hb 5 va 6 vf 7 vs 8 vb
     9 flags: bit 0 +hsync, bit 1 +vsync, bit 2 the 2:1 reduction
     10 x0 11 y0 12 fw 13 fh 14 panX (words) 15 panY (rows)
     16 cursor on 17 x 18 y 19 shape
     20 N, the pixel clocks captured from the frame start
     21 the capture index at which the bench moves the cursor (0 none)
     22 on 23 x 24 y 25 shape (the move)
     32 + 16 s + r: shape s row r, mask << 16 | image
  win_tmds.bin  N words of 4 bytes, big-endian:
     bit 31 the frame-start mark, [29:20] channel 2 (red),
     [19:10] channel 1 (green), [9:0] channel 0 (blue)

Use:
    python3 -I psi/winscan.py cases                  (the bench cases)
    python3 -I psi/winscan.py stream CASE > STREAM   (its drawing stream)
    python3 -I psi/winscan.py config CASE > win_scan.hex
    python3 -I psi/winscan.py check CASE FRAME.pbm win_tmds.bin
    python3 -I psi/winscan.py encvec SEED > IN.hex   (encoder bench input:
                                                      the count, then
                                                      DE<<10|C<<8|D a line)
    python3 -I psi/winscan.py enccheck IN.hex OUT.hex
    python3 -I psi/winscan.py sercheck win_ser_px.hex win_ser.bin
"""
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import winfb as F  # noqa: E402
import wintmds as T  # noqa: E402

BORDER, BLACK, WHITE = 0x20, 0x00, 0xff

# name, clock kHz, ha hf hs hb, va vf vs vb, +h, +v, x0 y0 fw fh, half
MODES = {
    0: dict(name='1920x1080@30 letterbox (CEA-861 VIC 34)', khz=74250,
            ha=1920, hf=88, hs=44, hb=148, va=1080, vf=4, vs=5, vb=36,
            hpos=True, vpos=True, x0=320, y0=28, fw=1280, fh=1024,
            half=False),
    1: dict(name='1280x1024@60 (VESA DMT 0x23)', khz=108000,
            ha=1280, hf=48, hs=112, hb=248, va=1024, vf=1, vs=3, vb=38,
            hpos=True, vpos=True, x0=0, y0=0, fw=1280, fh=1024,
            half=False),
    2: dict(name='1280x1024 reduced blanking @49.4 (OURS)', khz=75000,
            ha=1280, hf=48, hs=32, hb=80, va=1024, vf=3, vs=7, vb=20,
            hpos=True, vpos=False, x0=0, y0=0, fw=1280, fh=1024,
            half=False),
    3: dict(name='640x480@60 2:1 (VESA DMT 0x04)', khz=25175,
            ha=640, hf=16, hs=96, hb=48, va=480, vf=10, vs=2, vb=33,
            hpos=False, vpos=False, x0=0, y0=0, fw=640, fh=480,
            half=True),
}
# the drm_edid.c lines, as printed there (sync start, sync end, total)
DRM = {0: (2008, 2052, 2200, 1084, 1089, 1125),
       1: (1328, 1440, 1688, 1025, 1028, 1066),
       3: (656, 752, 800, 490, 492, 525)}


def totals(m):
    return (m['ha'] + m['hf'] + m['hs'] + m['hb'],
            m['va'] + m['vf'] + m['vs'] + m['vb'])


# ------------------------------------------------------------ timing
_LC = {}


def line_ctrl(m, vy):
    """The per-clock (de, C1C0 of channel 0) of line vy, as two lists
    (memoised per mode and line kind: active/blank, vsync or not)."""
    ht, _vt = totals(m)
    vact = m['va'] + m['vf'] <= vy < m['va'] + m['vf'] + m['vs']
    key = (tuple(sorted((k, v) for k, v in m.items())), vy < m['va'], vact)
    if key not in _LC:
        _LC[key] = _line_ctrl(m, vy, vact, ht)
    return _LC[key]


def _line_ctrl(m, vy, vact, ht):
    vlev = vact if m['vpos'] else not vact
    de, c = [], []
    for hx in range(ht):
        hact = m['ha'] + m['hf'] <= hx < m['ha'] + m['hf'] + m['hs']
        hlev = hact if m['hpos'] else not hact
        de.append(hx < m['ha'] and vy < m['va'])
        c.append(int(vlev) << 1 | int(hlev))
    return de, c


# -------------------------------------------------------------- view
def frame_rows(pbm):
    """The rows of the first PBM image as ints (dot x = bit 1279 - x)."""
    hdr = len(F.PBM_HEADER)
    if pbm[:hdr] != F.PBM_HEADER:
        raise ValueError('not a 1280x1024 P4 image')
    return [int.from_bytes(pbm[hdr + 160 * y:hdr + 160 * (y + 1)], 'big')
            for y in range(F.H)]


def frame_dot(rows, x, y):
    if x >= F.W or y >= F.H:
        return 0
    return (rows[y] >> (F.W - 1 - x)) & 1


def window_dot(m, pan, rows, u, v):
    px, py = 16 * pan[0], pan[1]
    if not m['half']:
        return frame_dot(rows, u + px, v + py)
    x, y = 2 * u + px, 2 * v + py
    return (frame_dot(rows, x, y) | frame_dot(rows, x + 1, y) |
            frame_dot(rows, x, y + 1) | frame_dot(rows, x + 1, y + 1))


def line_levels(m, pan, rows, cur, shapes, vy):
    """The active levels of line vy (a list of ha bytes; [] if blank)."""
    if vy >= m['va']:
        return []
    out = [BORDER] * m['ha']
    v = vy - m['y0']
    if not 0 <= v < m['fh']:
        return out
    on, cx, cy, sh = cur
    for u in range(m['fw']):
        hx = m['x0'] + u
        if hx >= m['ha']:
            break
        black = window_dot(m, pan, rows, u, v)
        du, dv = (u - cx) % 4096, (v - cy) % 2048
        if on and du < 16 and dv < 16:
            mask, img = shapes[sh][dv]
            if (mask >> (15 - du)) & 1:
                black = (img >> (15 - du)) & 1
        out[hx] = BLACK if black else WHITE
    return out


# ------------------------------------------------------------ cursor
ARROW = ['X...............', 'XX..............', 'X.X.............',
         'X..X............', 'X...X...........', 'X....X..........',
         'X.....X.........', 'X......X........', 'X.......X.......',
         'X........X......', 'X.....XXXXX.....', 'X..X..X.........',
         'X.X.X..X........', 'XX..X..X........', 'X....X..X.......',
         '.....XXXX.......']        # OURS: '.' clear, 'X' black, mask = outline+fill


def arrow_shape():
    rows = []
    for r in ARROW:
        img = sum(1 << (15 - i) for i, ch in enumerate(r) if ch == 'X')
        # the mask: the black outline plus the white inside of the arrow
        first = r.find('X')
        last = r.rfind('X')
        mask = 0
        if first >= 0:
            for i in range(first, last + 1):
                mask |= 1 << (15 - i)
        rows.append((mask, img))
    return rows


def shapes_for(seed):
    """8 shapes: 0 the arrow, 1 a solid block, 2 a hollow box, 3 an
    asymmetric test pattern, the rest random."""
    rnd = random.Random(seed)
    s = [arrow_shape(), [(0xffff, 0xffff)] * 16,
         [(0xffff, 0xffff if r in (0, 15) else 0x8001) for r in range(16)],
         [((0xffff >> r) & 0xffff | 0x0001, 0xf0f0 >> (r % 5))
          for r in range(16)]]
    while len(s) < 8:
        s.append([(rnd.randrange(65536), rnd.randrange(65536))
                  for _ in range(16)])
    return s


# ------------------------------------------------------------- cases
def s_testcard(_seed):
    """Dots at the frame's four corners, edges on rows 0 and 1023 and
    columns 0 and 1279, a non-periodic pattern (catches a pixel, word
    or window slip and the bit order), 2x2 probes for the OR reduction,
    and text."""
    L = ['fill 0 0 1 1 set', 'fill 1279 0 1 1 set', 'fill 0 1023 1 1 set',
         'fill 1279 1023 1 1 set',
         'fill 3 0 1270 1 set', 'fill 5 1023 1260 1 set',
         'fill 0 4 1 1010 set', 'fill 1279 6 1 1000 set',
         'line 2 2 1277 1021 1 65535 set', 'line 1277 2 2 1021 1 52428 set']
    # non-periodic dots: x = k(k+1)/2, rows 20..60
    for k in range(50):
        x = (k * (k + 1) // 2) % 1280
        L.append('fill %d %d %d %d set' % (x, 20 + k % 41, 1 + k % 3, 1 + k % 2))
    # 2x2 probes: a single dot at each of the four positions of a block,
    # at both even and odd frame rows of the 2:1 view (rows >= 24 too)
    for i, (dx, dy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)]):
        for base in (100, 125, 961, 982):
            L.append('fill %d %d 1 1 set' % (200 + 8 * i + dx, base + dy))
    L += ['fill 600 500 77 33 set', 'fill 611 507 31 9 xor',
          'fill 1200 940 80 44 set']
    for i, c in enumerate(F.jis_text(F.LOGIN_PROMPT)):
        L.append('glyph 0 %d %d 300 set' % (c, 20 + 11 * i))
    for i, c in enumerate(F.jis_text('Shell>> ')):
        L.append('glyph 0 %d %d 960 copy' % (c, 640 + 11 * i))
    L.append('end')
    return '\n'.join(L)


def s_random(seed):
    return F._rand_stream(seed, 60, ['fill'] * 4 + ['copy'] * 2 +
                          ['line'] * 3 + ['glyph'] * 3)


def random_mode(rnd):
    half = rnd.random() < 0.4
    ha = rnd.randrange(32, 129)
    va = rnd.randrange(8, 41)
    m = dict(name='random', khz=0, ha=ha, hf=rnd.randrange(1, 9),
             hs=rnd.randrange(1, 9), hb=rnd.randrange(1, 9), va=va,
             vf=rnd.randrange(1, 4), vs=rnd.randrange(1, 4),
             vb=rnd.randrange(1, 4), hpos=rnd.random() < 0.5,
             vpos=rnd.random() < 0.5, half=half)
    m['x0'] = rnd.randrange(0, ha // 2)
    m['y0'] = rnd.randrange(0, va // 2)
    m['fw'] = rnd.randrange(1, ha - m['x0'] + 1)
    m['fh'] = rnd.randrange(max(1, (va - m['y0']) // 2), va - m['y0'] + 1)
    if rnd.random() < 0.3:      # a window wider than the active area
        m['fw'] = ha - m['x0'] + rnd.randrange(1, 20)
    return m


def case(name):
    """(stream text, mode dict, pan, cursor, shapes, extra lines, move)."""
    sh = shapes_for(7)
    if name in ('mode0', 'mode1', 'mode2', 'mode3', 'mode2_nocursor'):
        n = int(name[4])
        m = dict(MODES[n], table=n)
        stream = s_testcard(0)
        pan = (0, 0)
        move = None
        if n == 0:
            cur = (1, 640, 500, 0)
        elif n == 1:
            cur = (1, 0, 0, 3)                    # the window's corner
        elif n == 2:
            cur = (1, 1272, 1015, 3)              # clipped right and bottom
            move = (5000, (1, 700, 0, 2))         # effective next frame only
        else:
            pan = (0, 24)
            cur = (1, 630, 470, 0)                # clipped at the bottom right
        if name == 'mode2_nocursor':
            cur, move = (0, 100, 100, 1), None
        return stream, m, pan, cur, sh, 2, move
    if name.startswith('rand'):
        seed = int(name[4:])
        rnd = random.Random(1000 + seed)
        m = random_mode(rnd)
        pan = (rnd.randrange(0, 84), rnd.choice([rnd.randrange(0, 1030),
                                                 rnd.randrange(0, 40)]))
        cur = (1, rnd.randrange(-5, m['fw'] + 3) % 4096,
               rnd.randrange(-5, m['fh'] + 3) % 2048, rnd.randrange(8))
        ht, vt = totals(m)
        # the move lands before the next frame's lead start (the scan-out
        # pipeline is 17 clocks deep), so it shows from the next frame on
        move = (rnd.randrange(1, ht * vt - 64), (1, rnd.randrange(0, m['fw']),
                                           rnd.randrange(0, 3), rnd.randrange(8)))
        # the stream draws near the panned window so the view is not blank
        body = s_random(seed).rsplit('\n', 1)[0]      # without its end
        stream = body + \
            '\nfill %d %d 40 20 xor\nline %d %d %d %d 1 65535 xor\nend' % (
                16 * pan[0] % 1280, pan[1] % 1024, 16 * pan[0] % 1280,
                pan[1] % 1024, (16 * pan[0] + 90) % 1280, (pan[1] + 30) % 1024)
        return stream, m, pan, cur, sh, 3, move
    raise KeyError(name)


CASES = ['mode0', 'mode1', 'mode2', 'mode3', 'mode2_nocursor'] + \
    ['rand%d' % i for i in range(1, 13)]


def n_capture(m, extra):
    ht, vt = totals(m)
    return ht * vt + extra * ht


def config_words(name):
    _s, m, pan, cur, sh, extra, move = case(name)
    w = [0] * 160
    w[0] = m.get('table', 15)
    for i, k in enumerate(['ha', 'hf', 'hs', 'hb', 'va', 'vf', 'vs', 'vb']):
        w[1 + i] = m[k]
    w[9] = int(m['hpos']) | int(m['vpos']) << 1 | int(m['half']) << 2
    w[10], w[11], w[12], w[13] = m['x0'], m['y0'], m['fw'], m['fh']
    w[14], w[15] = pan
    w[16:20] = cur
    w[20] = n_capture(m, extra)
    if move:
        w[21] = move[0]
        w[22:26] = move[1]
    for s in range(8):
        for r in range(16):
            mask, img = sh[s][r]
            w[32 + 16 * s + r] = mask << 16 | img
    return w


# ------------------------------------------------------------- check
class Fail(Exception):
    pass


def expected_words(m, pan, rows, cur, shapes, extra, move):
    """The capture as the reference produces it: (words, cursor per
    line) -- words packed as win_tmds.bin, encoded by wintmds.encode."""
    ht, vt = totals(m)
    out = []
    cnt = [0, 0, 0]
    n = 0
    cur_now = cur
    pending = None
    lines = [(f, vy) for f in (0,) for vy in range(vt)] + \
        [(1, vy) for vy in range(extra)]
    for f, vy in lines:
        if f == 1 and vy == 0 and pending:
            cur_now = pending
        lev = line_levels(m, pan, rows, cur_now, shapes, vy)
        de, c = line_ctrl(m, vy)
        for hx in range(ht):
            if move and n == move[0]:
                pending = move[1]
            if de[hx]:
                d = lev[hx]
                t0 = T.enc_table(cnt[0])[d]
                t1 = T.enc_table(cnt[1])[d]
                t2 = T.enc_table(cnt[2])[d]
                s0, cnt[0] = t0
                s1, cnt[1] = t1
                s2, cnt[2] = t2
            else:
                s0, s1, s2 = T.CTRL[c[hx]], T.CTRL[0], T.CTRL[0]
                cnt = [0, 0, 0]
            start = 1 if (vy == 0 and hx == 0) else 0
            out.append(start << 31 | s2 << 20 | s1 << 10 | s0)
            n += 1
    return out


def decode_check(m, pan, rows, cur, shapes, extra, move, words):
    """The decoder-side checks, independent of the encoder: every
    character decodes, the three channels agree, control characters
    only in blanking with C = 00 on channels 1 and 2, channel 0's
    C1C0 = the timing model's sync levels clock by clock, the active
    data equal to the view, the frame-start mark once a frame, the
    running disparity within the bound of the exhaustive search.
    Returns a dict of counts for the report."""
    ht, vt = totals(m)
    states, syms = T.reachable()
    bound = max(abs(s) for s in states)
    if len(words) != n_capture(m, extra):
        raise Fail('captured %d clocks, expected %d' %
                   (len(words), n_capture(m, extra)))
    n = 0
    cur_now, pending = cur, None
    disp = [0, 0, 0]
    worst = 0
    hs_edges = vs_lines = de_px = 0
    for f, vy in [(0, y) for y in range(vt)] + [(1, y) for y in range(extra)]:
        if f == 1 and vy == 0 and pending:
            cur_now = pending
        lev = line_levels(m, pan, rows, cur_now, shapes, vy)
        de, c = line_ctrl(m, vy)
        prev_h = None
        for hx in range(ht):
            if move and n == move[0]:
                pending = move[1]
            w = words[n]
            start = w >> 31
            if start != (1 if hx == 0 and vy == 0 else 0):
                raise Fail('frame-start mark at clock %d (line %d, x %d): %d'
                           % (n, vy, hx, start))
            s = [w & 1023, (w >> 10) & 1023, (w >> 20) & 1023]
            ctl = [T.DEC_CTRL[q] for q in s]
            if de[hx]:
                if any(q not in syms for q in s):
                    raise Fail('line %d x %d: a character no encoder makes: %s'
                               % (vy, hx, ['%03x' % q for q in s]))
                d = [T.DEC_DATA[q] for q in s]
                if d[0] != d[1] or d[1] != d[2]:
                    raise Fail('line %d x %d: channels differ %s' % (vy, hx, d))
                if d[0] not in (BLACK, WHITE, BORDER):
                    raise Fail('line %d x %d: level %02x' % (vy, hx, d[0]))
                if d[0] != lev[hx]:
                    raise Fail('line %d x %d: pixel %02x, the view has %02x '
                               '(frame %d)' % (vy, hx, d[0], lev[hx], f))
                for i in range(3):
                    disp[i] += T.DISP[s[i]]
                    worst = max(worst, abs(disp[i]))
                de_px += 1
            else:
                if None in ctl:
                    raise Fail('line %d x %d: blanking, not a control '
                               'character: %s' % (vy, hx, ['%03x' % q for q in s]))
                if ctl[1] != 0 or ctl[2] != 0:
                    raise Fail('line %d x %d: CTL bits %s on channels 1, 2'
                               % (vy, hx, ctl[1:]))
                if ctl[0] != c[hx]:
                    raise Fail('line %d x %d: C1C0 %d%d, the timing model '
                               'has %d%d' % (vy, hx, ctl[0] >> 1, ctl[0] & 1,
                                             c[hx] >> 1, c[hx] & 1))
                disp = [0, 0, 0]
            hlev = ctl[0] & 1 if ctl[0] is not None else None
            if f == 0 and hlev is not None and prev_h is not None and \
                    hlev != prev_h and hlev == int(m['hpos']):
                hs_edges += 1
            if f == 0 and hx == 0 and ctl[0] is not None and \
                    (ctl[0] >> 1) == int(m['vpos']):
                vs_lines += 1
            prev_h = hlev
            n += 1
    if worst > bound:
        raise Fail('running disparity %d beyond the bound %d' % (worst, bound))
    return dict(hsync=hs_edges, vsync_lines=vs_lines, de=de_px, worst=worst,
                bound=bound)


def check(name, pbm_path, bin_path):
    _s, m, pan, cur, sh, extra, move = case(name)
    with open(pbm_path, 'rb') as fh:
        rows = frame_rows(fh.read())
    with open(bin_path, 'rb') as fh:
        raw = fh.read()
    words = [v for (v,) in struct.iter_unpack('>I', raw)]
    r = decode_check(m, pan, rows, cur, sh, extra, move, words)
    ht, vt = totals(m)
    if r['hsync'] != vt:
        raise Fail('%d hsync pulses in the frame, expected %d' % (r['hsync'], vt))
    if r['vsync_lines'] != m['vs']:
        raise Fail('%d vsync lines, expected %d' % (r['vsync_lines'], m['vs']))
    if r['de'] != m['ha'] * m['va'] + m['ha'] * min(extra, m['va']):
        raise Fail('%d active pixels' % r['de'])
    exp = expected_words(m, pan, rows, cur, sh, extra, move)
    if exp != words:
        i = next(k for k in range(len(exp)) if exp[k] != words[k])
        raise Fail('the characters differ from wintmds.encode at clock %d '
                   '(line %d, x %d): %08x, expected %08x' %
                   (i, i // ht, i % ht, words[i], exp[i]))
    return '%s: %dx%d total %dx%d, %d clocks, %d hsync, %d vsync lines, ' \
           'disparity <= %d (bound %d), characters = wintmds.encode' % (
               name, m['ha'], m['va'], ht, vt, len(words), r['hsync'],
               r['vsync_lines'], r['worst'], r['bound'])


# --------------------------------------------- the encoder's own bench
def enc_vectors(seed):
    """(de, C1C0, D) triples: every byte from cnt 0 and from the other
    reachable states, long constant runs, random data with blanking
    bursts, control characters all four."""
    rnd = random.Random(seed)
    v = []
    for d in range(256):                    # every byte after a blank
        v += [(0, 0, 0), (1, 0, d)]
    for lead in (0x00, 0xff, 0x0f, 0x55, 0x01, 0xfe):
        for d in range(256):                # every byte at other cnt values
            v += [(0, rnd.randrange(4), 0), (1, 0, lead), (1, 0, lead),
                  (1, 0, d), (1, 0, d)]
    for d in (0x00, 0xff, 0x20, 0x10, 0xef, 0x7f, 0x80, 0x0b):
        v += [(1, 0, d)] * 64 + [(0, 3, 0)]
    for _ in range(6000):
        if rnd.random() < 0.05:
            v += [(0, rnd.randrange(4), rnd.randrange(256))] * rnd.randrange(1, 5)
        v.append((1, rnd.randrange(4), rnd.randrange(256)))
    return v


def enc_check(in_path, out_path):
    with open(in_path) as fh:
        vec = [int(x, 16) for x in fh.read().split()][1:]
    with open(out_path) as fh:
        got = [int(x, 16) for x in fh.read().split()]
    if len(got) != len(vec):
        raise Fail('%d characters for %d inputs' % (len(got), len(vec)))
    _st, syms = T.reachable()
    cnt = disp = worst = 0
    for i, (x, q) in enumerate(zip(vec, got)):
        de, c, d = x >> 10, (x >> 8) & 3, x & 255
        e, cnt = T.encode(cnt, de, c, d)
        if q != e:
            raise Fail('input %d (de %d C %d D %02x): %03x, expected %03x'
                       % (i, de, c, d, q, e))
        if de:
            if T.decode(q, True) != ('d', d) or q not in syms:
                raise Fail('input %d: does not decode' % i)
            disp += T.disparity(q)
            worst = max(worst, abs(disp))
        else:
            disp = 0
    return '%d characters = wintmds.encode, running disparity <= %d' % (
        len(got), worst)


# ---------------------------------------- the serializer's own bench
CLOCK_CHAR = 0b0000011111       # the clock lane: five ones, five zeros


def ser_check(px_path, bin_path):
    """bsv/WinTmdsSerTb: rebuild each lane's serial stream (D0 then D1
    each shift clock; bit 0 of a character first), find the character
    boundary on the clock lane, and require each data lane to carry the
    logged pixel-domain characters exactly, all lanes at the same
    boundary and latency."""
    with open(px_path) as fh:
        px = [[int(x, 16) for x in ln.split()] for ln in fh if ln.strip()]
    with open(bin_path, 'rb') as fh:
        raw = fh.read()
    bits = [[], [], [], []]
    for b in raw:
        for lane in range(4):
            v = (b >> (2 * lane)) & 3
            bits[lane] += [v & 1, v >> 1]

    def chars(lane, off):
        bs = bits[lane]
        return [sum(bs[off + 10 * k + i] << i for i in range(10))
                for k in range((len(bs) - off) // 10)]

    # the clock lane: after the serializer's first load, one boundary
    # gives the clock character throughout
    offs = [o for o in range(10)
            if all(c == CLOCK_CHAR for c in chars(3, o)[2:])]
    if len(offs) != 1:
        raise Fail('clock lane: %d boundaries give a steady clock character'
                   % len(offs))
    off = offs[0]
    lat = None
    for lane in range(3):
        got = chars(lane, off)
        want = [p[lane] for p in px]
        hits = [L for L in range(-4, 12)
                if all(got[k] == want[k - L] for k in range(max(L, 0) + 2,
                                                            len(want) + L - 2)
                       if 0 <= k < len(got))]
        if len(hits) != 1:
            raise Fail('lane %d: the logged characters appear at %d latencies '
                       'at the clock boundary %d' % (lane, len(hits), off))
        if lat is None:
            lat = hits[0]
        elif hits[0] != lat:
            raise Fail('lane %d at latency %d, lane 0 at %d' % (lane, hits[0], lat))
    return '%d shift clocks, %d characters a lane = the encoders\' (clock ' \
           'boundary at bit %d, latency %d characters)' % (
               len(raw), len(px), off, lat)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    try:
        if cmd == 'cases':
            print('\n'.join(CASES))
        elif cmd == 'stream':
            sys.stdout.write(F.assemble(case(argv[1])[0]))
        elif cmd == 'config':
            sys.stdout.write(''.join('%08x\n' % w for w in config_words(argv[1])))
        elif cmd == 'check':
            print(check(argv[1], argv[2], argv[3]))
        elif cmd == 'encvec':
            v = enc_vectors(int(argv[1]))
            print('%04x' % len(v))
            for de, c, d in v:
                print('%03x' % (de << 10 | c << 8 | d))
        elif cmd == 'enccheck':
            print(enc_check(argv[1], argv[2]))
        elif cmd == 'sercheck':
            print(ser_check(argv[1], argv[2]))
        else:
            print(__doc__)
            return 2
    except Fail as e:
        print('MISMATCH %s' % e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
