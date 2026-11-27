#!/usr/bin/env python3
"""The window input path's reference: tables, PS/2 framing, event records
(window hardware H5, docs/simpos/window_hardware_plan.md §3.1-§3.3).

ALL OURS except where a line says otherwise: the PSI's keyboard and mouse
hung off its console processor (TM-153 PDF p23), and nothing of their
wire protocol is held.  The board takes a PS/2 keyboard (or mouse) on US2
through a USB-OTG + USB-PS/2 adapter (the ULX3S manual's suggestion).

TWO TABLES, kept apart so each is checked on its own:
  HOST  a host key, named by its USB HID usage ID (HID Usage Tables 1.12
        §10, page 0x07: SECONDARY, the published standard; SDL2's
        SDL_Scancode values are the same numbers), to the PS/2 scan code
        set 2 make code (0xE0-prefixed or not).  The break is F0 before
        the code's last byte.  This is the KEYBOARD's table: the bench's
        PS/2 device model and bsv/WinHostDev.c use it; the C copy is
        checked against this one (`hostcheck`).
  KEYS  the §3.1 table, PS/2 set 2 to the PSI's keys: printing ASCII to
        full-width JIS X 0208 (row 3 digits and letters, row 1
        punctuation, 16#2121 space; the codes are those psi/kl0.py's Str
        stores, checked by `jischeck`), named keys `key#` (indices
        below), `pf#0`-`pf#18`, the modifiers.  This is the BOARD's table:
        `bsv` writes bsv/WinKeyTable.bsv from it (`--check` compares).
  The set 2 codes are the IBM PC AT set 2 as commonly published
  (SECONDARY: no IBM manual is held here).

EVENT RECORDS (OURS; what bsv/WinInput.bsv emits and the link carries up
as TYPE 3, LEN 10): KIND, A (16), B (16), C (16), FLAGS, T (16), big-endian.
  KIND 1 key, JIS      A the JIS code; FLAGS bit 0 Ctrl held, bit 1 Alt held
  KIND 2 key, named    A the name's index in NAMES
  KIND 3 pf            A 0-18
  KIND 4 button        A 0 left, 1 middle, 2 right; B X, C Y; FLAGS bit 0 down
  KIND 5 move          B X, C Y (clamped to the 1,280 x 1,024 frame)
  KIND 6 error         A the code: 1 parity, 2 stop bit, 3 a frame cut off
                       (no clock edge for the timeout), 4 a scan code the
                       table lacks (B the code, FLAGS bit 0 its E0 prefix),
                       5 a mouse packet whose first byte lacks bit 3;
                       FLAGS bit 7 the mouse's receiver (codes 1-3)
  T is the receiver's millisecond count mod 65,536 at the record.
  The mouse starts at (640, 472), the coordinator stand-in's start
  (psi/standin/coordinator.esp mouse_x/mouse_y), and PS/2's Y counts up,
  the frame's down.  Double clicks are NOT classified here (§3.2: the
  handler's job): tools/win_kl0_host.py does it for the kl0 host.

SCRIPTS.  A high-level input script, one action a line:
    type TEXT            the text's keys (Shift around capitals and the
                         shifted punctuation)
    key NAME             one key: enter, bs, tab, esc, del, up, down, left,
                         right, f1-f12, insert, kpenter
    shiftkey NAME        the same with Shift held
    ctrlkey CH, altkey CH  the key of CH (unshifted) with left Ctrl / Alt held
    down KEY, up KEY     one make or break (KEY a character's key, a NAME,
                         shift, ctrl or alt): a held key repeats by its
                         makes (typematic), so make and break differ
    click B X Y          move to (X, Y), then B (l m r) down and up
    moveto X Y           move only
    wait MS
    fault DEV BYTE KIND  a raw byte on DEV (kbd, mouse) with KIND none,
                         parity, stop, cut (8 bits, then silence), glitch
                         (a one-cycle clock pulse inside the byte: received)
`expand` turns it into the primitive host script bsv/WinHostDev.c reads
(kd/ku USAGE, m DX DY BUTTONS, w MS, kraw/mraw BYTE FAULT; header of
WinHostDev.c), `bytes` into the two devices' byte streams for
bsv/WinInputTb.bsv, `expect` into the records the receivers must emit.

Use:
    python3 -I tools/wininput.py bsv OUT.bsv | --check OUT.bsv
    python3 -I tools/wininput.py expand SCRIPT OUT.hostscript
    python3 -I tools/wininput.py bytes SCRIPT KBD.hex MOUSE.hex [N.hex]
    python3 -I tools/wininput.py expect SCRIPT OUT.records
    python3 -I tools/wininput.py compare WANT.records GOT.records
    python3 -I tools/wininput.py hostcheck DUMP      (WinHostDev.c's table dump)
    python3 -I tools/wininput.py jischeck | selftest
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

NAMES = ['lf', 'cr', 'del', 'enter', 'esc', 'tab', 'bs', 'bell', 'up', 'down',
         'left', 'right', 'abort', 'help']

# printing ASCII -> JIS X 0208 (row 1 punctuation, row 3 alphanumerics)
PUNCT = {'!': 0x212a, '"': 0x2149, '#': 0x2174, '$': 0x2170, '%': 0x2173, '&': 0x2175,
         "'": 0x2147, '(': 0x214a, ')': 0x214b, '*': 0x2176, '+': 0x215c, ',': 0x2124,
         '-': 0x215d, '.': 0x2125, '/': 0x213f, ':': 0x2127, ';': 0x2128, '<': 0x2163,
         '=': 0x2161, '>': 0x2164, '?': 0x2129, '@': 0x2177, '[': 0x214e, '\\': 0x2140,
         ']': 0x214f, '^': 0x2130, '_': 0x2132, '`': 0x212e, '{': 0x2150, '|': 0x2143,
         '}': 0x2151, '~': 0x2141, ' ': 0x2121}


def jis(ch):
    if '0' <= ch <= '9':
        return 0x2330 + ord(ch) - 0x30
    if 'A' <= ch <= 'Z':
        return 0x2341 + ord(ch) - 0x41
    if 'a' <= ch <= 'z':
        return 0x2361 + ord(ch) - 0x61
    return PUNCT[ch]


# ---- KEYS: set 2 -> the PSI's keys (the §3.1 table) ----------------------
# (e0, code) -> ('chr', unshifted, shifted) | ('name', n) | ('pf', n, shifted pf or None)
#             | ('mod', 'shift'|'ctrl'|'alt') | ('nop',)
_LETTERS = dict(zip('abcdefghijklmnopqrstuvwxyz',
                    [0x1c, 0x32, 0x21, 0x23, 0x24, 0x2b, 0x34, 0x33, 0x43, 0x3b, 0x42, 0x4b, 0x3a,
                     0x31, 0x44, 0x4d, 0x15, 0x2d, 0x1b, 0x2c, 0x3c, 0x2a, 0x1d, 0x22, 0x35, 0x1a]))
_DIGITS = dict(zip('1234567890', [0x16, 0x1e, 0x26, 0x25, 0x2e, 0x36, 0x3d, 0x3e, 0x46, 0x45]))
_SHIFTED_DIGITS = dict(zip('1234567890', '!@#$%^&*()'))
_PUNCT_KEYS = {0x4e: ('-', '_'), 0x55: ('=', '+'), 0x54: ('[', '{'), 0x5b: (']', '}'),
               0x5d: ('\\', '|'), 0x4c: (';', ':'), 0x52: ("'", '"'), 0x0e: ('`', '~'),
               0x41: (',', '<'), 0x49: ('.', '>'), 0x4a: ('/', '?'), 0x29: (' ', ' ')}
_FKEYS = [0x05, 0x06, 0x04, 0x0c, 0x03, 0x0b, 0x83, 0x0a, 0x01, 0x09, 0x78, 0x07]


def keys_table():
    t = {}
    for ch, c in _LETTERS.items():
        t[(0, c)] = ('chr', ch, ch.upper())
    for ch, c in _DIGITS.items():
        t[(0, c)] = ('chr', ch, _SHIFTED_DIGITS[ch])
    for c, (a, b) in _PUNCT_KEYS.items():
        t[(0, c)] = ('chr', a, b)
    # named keys (§3.1: Enter cr, keypad Enter enter, Backspace bs, Delete
    # del, the arrows, Insert help, Pause abort (OURS: Pause's E1 sequence
    # is taken by its E1 14 77 make), Esc, Tab)
    for e0, c, n in ((0, 0x5a, 'cr'), (1, 0x5a, 'enter'), (0, 0x66, 'bs'), (1, 0x71, 'del'),
                     (1, 0x75, 'up'), (1, 0x72, 'down'), (1, 0x6b, 'left'), (1, 0x74, 'right'),
                     (1, 0x70, 'help'), (0, 0x76, 'esc'), (0, 0x0d, 'tab'), (2, 0x77, 'abort')):
        t[(e0, c)] = ('name', NAMES.index(n))
    # F1-F12 -> pf#0-pf#11, Shift-F1..F7 -> pf#12-pf#18 (§3.1)
    for i, c in enumerate(_FKEYS):
        t[(0, c)] = ('pf', i, 12 + i if i < 7 else None)
    for e0, c, m in ((0, 0x12, 'shift'), (0, 0x59, 'shift'), (0, 0x14, 'ctrl'), (1, 0x14, 'ctrl'),
                     (0, 0x11, 'alt'), (1, 0x11, 'alt')):
        t[(e0, c)] = ('mod', m)
    t[(0, 0x58)] = ('nop',)        # Caps Lock: OURS, no effect
    return t


KEYS = keys_table()


def key_event(entry, shift, ctrl, alt):
    """The record (kind, a, flags) for a make of ENTRY, or None (modifier)."""
    k = entry[0]
    if k == 'chr':
        ch = entry[2] if shift else entry[1]
        if ctrl and ch.lower() == 'j':
            return (2, NAMES.index('lf'), 0)
        if ctrl and ch.lower() == 'g':
            return (2, NAMES.index('bell'), 0)
        return (1, jis(ch), (1 if ctrl else 0) | (2 if alt else 0))
    if k == 'name':
        return (2, entry[1], 0)
    if k == 'pf':
        if shift and entry[2] is not None:
            return (3, entry[2], 0)
        return (3, entry[1], 0)
    return None


# ---- HOST: HID usage -> set 2 (the keyboard's table) ---------------------
def host_table():
    t = {}
    for i, ch in enumerate('abcdefghijklmnopqrstuvwxyz'):
        t[0x04 + i] = (0, _LETTERS[ch])
    for i, ch in enumerate('1234567890'):
        t[0x1e + i] = (0, _DIGITS[ch])
    for u, c in ((0x28, (0, 0x5a)), (0x29, (0, 0x76)), (0x2a, (0, 0x66)), (0x2b, (0, 0x0d)),
                 (0x2c, (0, 0x29)), (0x2d, (0, 0x4e)), (0x2e, (0, 0x55)), (0x2f, (0, 0x54)),
                 (0x30, (0, 0x5b)), (0x31, (0, 0x5d)), (0x33, (0, 0x4c)), (0x34, (0, 0x52)),
                 (0x35, (0, 0x0e)), (0x36, (0, 0x41)), (0x37, (0, 0x49)), (0x38, (0, 0x4a)),
                 (0x39, (0, 0x58)), (0x49, (1, 0x70)), (0x4c, (1, 0x71)), (0x4f, (1, 0x74)),
                 (0x50, (1, 0x6b)), (0x51, (1, 0x72)), (0x52, (1, 0x75)), (0x58, (1, 0x5a)),
                 (0xe0, (0, 0x14)), (0xe1, (0, 0x12)), (0xe2, (0, 0x11)), (0xe4, (1, 0x14)),
                 (0xe5, (0, 0x59)), (0xe6, (1, 0x11))):
        t[u] = c
    for i, c in enumerate(_FKEYS):
        t[0x3a + i] = (0, c)
    return t


HOST = host_table()
PAUSE = 0x48                    # its make is E1 14 77 E1 F0 14 F0 77, no break


def host_bytes(usage, down):
    if usage == PAUSE:
        return [0xe1, 0x14, 0x77, 0xe1, 0xf0, 0x14, 0xf0, 0x77] if down else []
    e0, c = HOST[usage]
    return ([0xe0] if e0 else []) + ([] if down else [0xf0]) + [c]


USAGE_OF = {}
for _u, (_e, _c) in HOST.items():
    USAGE_OF[(_e, _c)] = _u
NAMED_USAGE = {'enter': 0x28, 'esc': 0x29, 'bs': 0x2a, 'tab': 0x2b, 'insert': 0x49, 'del': 0x4c,
               'right': 0x4f, 'left': 0x50, 'down': 0x51, 'up': 0x52, 'kpenter': 0x58,
               'pause': PAUSE}
for _i in range(12):
    NAMED_USAGE['f%d' % (_i + 1)] = 0x3a + _i
LSHIFT = 0xe1


def char_usage(ch):
    """(usage, shift) for a printing character."""
    for (e0, c), ent in KEYS.items():
        if ent[0] == 'chr' and not e0:
            if ent[1] == ch:
                return USAGE_OF[(0, c)], False
            if ent[2] == ch:
                return USAGE_OF[(0, c)], True
    raise ValueError('no key types %r' % ch)


# ---- scripts --------------------------------------------------------------
MOUSE0 = (640, 472)
FW, FH = 1280, 1024
FAULTS = {'none': 0, 'parity': 1, 'stop': 2, 'cut': 3, 'glitch': 4}
BUTTONS = {'l': 0, 'm': 1, 'r': 2}
GLITCH = 4                      # a clock glitch the filter removes: the byte is good


def expand(text):
    """The primitive host script: [('kd'|'ku', usage) | ('m', dx, dy, btns) |
    ('w', ms) | ('kraw'|'mraw', byte, fault)]"""
    out = []
    pos = list(MOUSE0)
    btns = 0

    def press(u, shift=False):
        if shift:
            out.append(('kd', LSHIFT))
        out.append(('kd', u))
        out.append(('ku', u))
        if shift:
            out.append(('ku', LSHIFT))

    def moveto(x, y):
        while (x, y) != tuple(pos):
            dx = max(-255, min(255, x - pos[0]))
            dy = max(-255, min(255, y - pos[1]))
            pos[0] += dx
            pos[1] += dy
            out.append(('m', dx, -dy, btns))        # PS/2's Y counts up
    for ln in text.splitlines():
        w = ln.split('#', 1)[0].split() if not ln.lstrip().startswith('type ') else ln.split(None, 1)
        if not w:
            continue
        op = w[0]
        if op == 'type':
            for ch in w[1].rstrip('\n'):
                u, sh = char_usage(ch)
                press(u, sh)
        elif op == 'key':
            press(NAMED_USAGE[w[1]])
        elif op == 'shiftkey':
            press(NAMED_USAGE[w[1]], True)
        elif op in ('down', 'up'):
            k = w[1]
            u = {'shift': LSHIFT, 'ctrl': 0xe0, 'alt': 0xe2}.get(k) or NAMED_USAGE.get(k) \
                or char_usage(k)[0]
            out.append(('kd' if op == 'down' else 'ku', u))
        elif op in ('ctrlkey', 'altkey'):
            m = 0xe0 if op == 'ctrlkey' else 0xe2       # left Ctrl, left Alt
            out.append(('kd', m))
            press(char_usage(w[1])[0])
            out.append(('ku', m))
        elif op == 'moveto':
            moveto(int(w[1]), int(w[2]))
        elif op == 'click':
            moveto(int(w[2]), int(w[3]))
            b = 1 << BUTTONS[w[1]]
            btns |= b
            out.append(('m', 0, 0, btns))
            btns &= ~b
            out.append(('m', 0, 0, btns))
        elif op == 'wait':
            out.append(('w', int(w[1])))
        elif op == 'fault':
            out.append(('kraw' if w[1] == 'kbd' else 'mraw', int(w[2], 0), FAULTS[w[3]]))
        else:
            raise ValueError('script line %r' % ln)
    return out


def write_host(prims, path):
    with open(path, 'w') as f:
        for p in prims:
            if p[0] in ('kd', 'ku'):
                f.write('%s %02x\n' % p)
            elif p[0] == 'm':
                f.write('m %d %d %d\n' % p[1:])
            elif p[0] == 'w':
                f.write('w %d\n' % p[1])
            else:
                f.write('%s %02x %d\n' % p)
        f.write('end\n')


def mouse_packet(dx, dy, btns):
    b0 = 0x08 | (btns & 7) | (0x10 if dx < 0 else 0) | (0x20 if dy < 0 else 0)
    return [b0, dx & 0xff, dy & 0xff]


def device_bytes(prims):
    """The two devices' byte streams [(byte, fault, ms to wait before it)];
    a wait delays both devices' next byte."""
    kbd, mouse = [], []
    pend = {'k': 0, 'm': 0}
    for p in prims:
        if p[0] == 'w':
            pend['k'] += p[1]
            pend['m'] += p[1]
            continue
        if p[0] in ('kd', 'ku'):
            seq, dst, d = [(b, 0) for b in host_bytes(p[1], p[0] == 'kd')], kbd, 'k'
        elif p[0] == 'm':
            seq, dst, d = [(b, 0) for b in mouse_packet(*p[1:])], mouse, 'm'
        else:
            seq = [(p[1], p[2])]
            dst, d = (kbd, 'k') if p[0] == 'kraw' else (mouse, 'm')
        for k, (b, f) in enumerate(seq):
            dst.append((b, f, pend[d] if k == 0 else 0))
        pend[d] = 0
    return kbd, mouse


# ---- the receivers' model --------------------------------------------------
class KbdReceiver:
    """The keyboard receiver's model, a byte at a time (OURS; tools/
    simpos_live.py feeds it a viewer's keys as they come).  feed(BYTE,
    FAULT) -> the records [(kind, a, b, c, flags)] that byte completes."""

    def __init__(self):
        self.e0 = self.brk = False
        self.e1 = 0
        self.shift, self.ctrl, self.alt = set(), set(), set()

    def feed(self, b, f=0):
        if f and f != GLITCH:
            self.e0 = self.brk = False
            return [(6, f, 0, 0, 0)]
        if self.e1:
            # Pause: E1 14 77 E1 F0 14 F0 77; the 77 of its first three is the make
            self.e1 -= 1
            return [(2, NAMES.index('abort'), 0, 0, 0)] if self.e1 == 5 else []
        if b == 0xe1:
            self.e1 = 7
            return []
        if b == 0xe0:
            self.e0 = True
            return []
        if b == 0xf0:
            self.brk = True
            return []
        ent = KEYS.get((1 if self.e0 else 0, b))
        key = (self.e0, b)
        e0f, brkf = self.e0, self.brk
        self.e0 = self.brk = False
        if ent is None:
            return [(6, 4, b, 0, 1 if e0f else 0)]
        if ent[0] == 'mod':
            s = {'shift': self.shift, 'ctrl': self.ctrl, 'alt': self.alt}[ent[1]]
            (s.discard if brkf else s.add)(key)
            return []
        if brkf or ent[0] == 'nop':
            return []
        k, a, fl = key_event(ent, bool(self.shift), bool(self.ctrl), bool(self.alt))
        return [(k, a, 0, 0, fl)]


def receive_kbd(stream):
    """Records [(kind, a, b, c, flags)] the keyboard receiver emits."""
    r = KbdReceiver()
    out = []
    for b, f in stream:
        out += r.feed(b, f)
    return out


def receive_mouse(stream):
    out = []
    x, y = MOUSE0
    btns = 0
    pkt = []
    for b, f in stream:
        if f and f != GLITCH:
            out.append((6, f, 0, 0, 0x80))
            pkt = []
            continue
        if not pkt and not b & 0x08:
            out.append((6, 5, b, 0, 0x80))
            continue
        pkt.append(b)
        if len(pkt) < 3:
            continue
        b0, dx, dy = pkt
        pkt = []
        dx = dx - 256 if b0 & 0x10 else dx
        dy = dy - 256 if b0 & 0x20 else dy
        if dx or dy:
            x = max(0, min(FW - 1, x + dx))
            y = max(0, min(FH - 1, y - dy))
            out.append((5, 0, x, y, 0))
        for i in range(3):
            if (b0 ^ btns) & (1 << i):
                out.append((4, i, x, y, 1 if b0 & (1 << i) else 0))
        btns = b0 & 7
    return out


def expect(text):
    kbd, mouse = device_bytes(expand(text))
    return (receive_kbd([(b, f) for b, f, _w in kbd]),
            receive_mouse([(b, f) for b, f, _w in mouse]))


def fmt_record(r):
    return '%d %04x %04x %04x %02x' % r


def write_records(path, recs):
    with open(path, 'w') as f:
        for r in recs:
            f.write(fmt_record(r) + '\n')


def read_records(path):
    """[(kind, a, b, c, flags, t)] from a bench's record file (hex fields,
    t optional)."""
    out = []
    for ln in open(path):
        w = ln.split()
        if w:
            out.append(tuple([int(w[0])] + [int(v, 16) for v in w[1:]]))
    return out


def compare(want_path, got_path):
    want = read_records(want_path)
    got = read_records(got_path)
    split = lambda rs: ([r[:5] for r in rs if r[0] in (1, 2, 3) or (r[0] == 6 and not r[4] & 0x80)],  # noqa
                        [r[:5] for r in rs if r[0] in (4, 5) or (r[0] == 6 and r[4] & 0x80)])
    for name, w, g in zip(('keyboard', 'mouse'), split(want), split(got)):
        if w != g:
            k = next((i for i in range(min(len(w), len(g))) if w[i] != g[i]), min(len(w), len(g)))
            return '%s record %d: %s, expected %s (%d records, expected %d)' % (
                name, k, fmt_record(g[k]) if k < len(g) else 'none',
                fmt_record(w[k]) if k < len(w) else 'none', len(g), len(w))
    ts = [r[5] for r in got if len(r) > 5]
    if any(b < a for a, b in zip(ts, ts[1:])):
        return 'the time stamps go backwards'
    return ''


def write_bytes(path, stream):
    """One line a byte: FAULT (4 bits) WAIT_MS (12 bits) BYTE (8), hex."""
    with open(path, 'w') as f:
        n = 0
        for b, fl, w in stream:
            f.write('%06x\n' % ((fl << 20) | (min(w, 0xfff) << 8) | b))
            n += 1
        if n == 0:
            f.write('000000\n')
    return n


# ---- the generated BSV table -----------------------------------------------
def bsv_text():
    L = ['// WinKeyTable.bsv -- GENERATED by tools/wininput.py bsv; do not edit.',
         '// The §3.1 table (docs/simpos/window_hardware_plan.md): PS/2 scan code',
         '// set 2 to the PSI\'s keys.  ALL OURS (wininput.py\'s header).',
         'package WinKeyTable;', '',
         'typedef enum { KNone, KChr, KName, KPf, KShift, KCtrl, KAlt, KNop } WinKeyClass deriving (Bits, Eq);',
         'typedef struct { WinKeyClass cls; Bit#(16) lo; Bit#(16) hi; } WinKeyEntry deriving (Bits);',
         '// lo: the unshifted JIS (KChr), the name index (KName), the pf number',
         '// (KPf); hi: the shifted JIS, or the shifted pf number (16\'hffff: none)', '',
         'function WinKeyEntry winKey(Bool e0, Bit#(8) code);',
         '   WinKeyEntry r = WinKeyEntry { cls: KNone, lo: 0, hi: 0 };',
         '   case ({pack(e0), code})']
    for (e0, c), ent in sorted(KEYS.items()):
        if e0 == 2:
            continue                        # Pause: by its E1 sequence, in WinInput.bsv
        k = ent[0]
        if k == 'chr':
            v = 'KChr, lo: \'h%04x, hi: \'h%04x' % (jis(ent[1]), jis(ent[2]))
        elif k == 'name':
            v = 'KName, lo: %d, hi: 0' % ent[1]
        elif k == 'pf':
            v = 'KPf, lo: %d, hi: \'h%04x' % (ent[1], 0xffff if ent[2] is None else ent[2])
        elif k == 'mod':
            v = {'shift': 'KShift', 'ctrl': 'KCtrl', 'alt': 'KAlt'}[ent[1]] + ', lo: 0, hi: 0'
        else:
            v = 'KNop, lo: 0, hi: 0'
        L.append('      9\'h%03x: r = WinKeyEntry { cls: %s };' % ((e0 << 8) | c, v))
    L += ['   endcase', '   return r;', 'endfunction', '',
          'Bit#(16) nameLf = %d;' % NAMES.index('lf'),
          'Bit#(16) nameBell = %d;' % NAMES.index('bell'),
          'Bit#(16) nameAbort = %d;' % NAMES.index('abort'),
          'Bit#(16) jisJ = \'h%04x;' % jis('j'), 'Bit#(16) jisJu = \'h%04x;' % jis('J'),
          'Bit#(16) jisG = \'h%04x;' % jis('g'), 'Bit#(16) jisGu = \'h%04x;' % jis('G'),
          '', 'endpackage']
    return '\n'.join(L) + '\n'


def hostcheck(path):
    """WinHostDev.c's table, dumped as 'USAGE E0 CODE' lines, against HOST."""
    got = {}
    for ln in open(path):
        w = ln.split()
        if w:
            got[int(w[0], 16)] = (int(w[1]), int(w[2], 16))
    if got != HOST:
        miss = sorted(set(HOST) ^ set(got)) or [u for u in HOST if HOST[u] != got[u]]
        return 'WinHostDev.c\'s table differs from HOST at usages %s' % ' '.join('%02x' % u for u in miss[:8])
    return ''


def jischeck():
    sys.path.insert(0, os.path.join(HERE, '..', 'psi'))
    import kl0
    bad = [ch for ch in [chr(c) for c in range(0x20, 0x7f)] if kl0.Str(ch).codes() != [jis(ch)]]
    return 'JIS differs from kl0.Str for %r' % bad if bad else ''


def selftest():
    assert jischeck() == '', jischeck()
    k, m = expect('type aB.\nkey enter\nclick r 650 460\nfault kbd 0x1c parity\n')
    assert k == [(1, 0x2361, 0, 0, 0), (1, 0x2342, 0, 0, 0), (1, 0x2125, 0, 0, 0),
                 (2, NAMES.index('cr'), 0, 0, 0), (6, 1, 0, 0, 0)], k
    assert m == [(5, 0, 650, 460, 0), (4, 2, 650, 460, 1), (4, 2, 650, 460, 0)], m
    print('wininput selftest: OK')


def main(argv):
    if argv[:1] == ['bsv'] and len(argv) == 2:
        with open(argv[1], 'w') as f:
            f.write(bsv_text())
        return 0
    if argv[:1] == ['--check'] and len(argv) == 2:
        if open(argv[1]).read() != bsv_text():
            print('wininput --check: %s differs from the generator; run tools/wininput.py bsv' % argv[1])
            return 1
        print('wininput --check: %s is current' % argv[1])
        return 0
    if argv[:1] == ['expand'] and len(argv) == 3:
        write_host(expand(open(argv[1]).read()), argv[2])
        return 0
    if argv[:1] == ['bytes'] and len(argv) in (4, 5):
        kbd, mouse = device_bytes(expand(open(argv[1]).read()))
        nk, nm = write_bytes(argv[2], kbd), write_bytes(argv[3], mouse)
        if len(argv) == 5:
            with open(argv[4], 'w') as f:
                f.write('%x\n%x\n' % (nk, nm))
        print('wininput bytes: %d keyboard, %d mouse' % (nk, nm))
        return 0
    if argv[:1] == ['expect'] and len(argv) == 3:
        k, m = expect(open(argv[1]).read())
        write_records(argv[2], k + m)
        return 0
    if argv[:1] == ['compare'] and len(argv) == 3:
        r = compare(argv[1], argv[2])
        if r:
            print('wininput compare: ' + r)
            return 1
        print('wininput compare: %d records = the script\'s' % len(read_records(argv[1])))
        return 0
    if argv[:1] == ['hostcheck'] and len(argv) == 2:
        r = hostcheck(argv[1])
        print('wininput hostcheck: ' + (r or 'WinHostDev.c\'s table = HOST (%d keys)' % len(HOST)))
        return 1 if r else 0
    if argv == ['jischeck']:
        r = jischeck()
        print('wininput jischeck: ' + (r or 'printing ASCII = kl0.Str\'s JIS'))
        return 1 if r else 0
    if argv == ['selftest']:
        selftest()
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
