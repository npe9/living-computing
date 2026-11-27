#!/usr/bin/env python3
"""SIMPOS live on tools/winview: window plan M11's live view (OURS, 2026-11-26).

docs/simpos/window_environment_plan.md M11 planned "the browser canvas";
the viewer tools/winview (docs/simpos/winview_protocol.md) took its place.
This file is the software window stack's client of that viewer: the
stand-in SIMPOS (psi/fep_bridge.py PsiSide with no PIMOS: boot, login as
pmpsi, the coordinator, the status band) runs on kl0, and

  - SCREEN: every drawing command the device layer runs (psi/windev.py) is
    teed to a frame of this file's own (the device's `tees`), and the
    rows of that frame that changed go to the viewer as one `R` band at
    each quiet moment (and every FLUSH_MS while a long run draws);
  - INPUT: the viewer's raw events are the PSI's events by the same
    tables as the board's (tools/wininput.py): a key's HID usage -> its
    PS/2 set 2 bytes (HOST) -> the keyboard receiver (KEYS, Shift and
    Ctrl) -> the coordinator's {key, Code}; the mouse -> {mouse, Button,
    X, Y} and {move, X, Y}, double clicks classified by
    tools/win_kl0_host.py's Adapter (the plan §3.2 gives that to the
    handler process, whose stand-in does not classify; OURS here);
  - each batch of events goes on the coordinator's event stream at the
    next quiet moment (every PSI process waits), which is the path the
    scripted tests use (psi/test_espc.py Window.later_run): the launcher
    blocks in the PSI's idle hook until the viewer has something.

THE KEY CODES (the stand-ins' own, psi/espc.py KEY_CODES, OURS values
except key#lf, G2): a JIS character as its code; Ctrl with a letter its
ASCII control code (control#"x" = 24; the Pmacs stand-in binds C-f C-b
C-n C-p C-a C-e C-d C-k C-x C-c, and C-x C-s / C-x C-z); Return 13 (cr),
keypad Enter key#enter, Backspace 8 (bs), Delete 127 (del), Tab 9, Esc 27,
the arrows key#up/down/left/right, Insert key#help, Pause key#abort, F1-F12
pf#0-pf#11 and Shift-F1..F7 pf#12-pf#18 (wininput.py's §3.1 table);
Alt is not passed on (meta# keys are not stood in): the code goes alone.
OURS MOUSE ALTERNATES (for a Mac trackpad): Option (Alt) held with the
left button is the middle button (the window manipulator).  The system
menu is the PSI's: the right button twice (mouse#rr).

THE EVENT FILE (OURS), one event a line, MS the session's milliseconds:
    MS K DOWN USAGE      a key (USAGE hex), as winview's K
    MS M X Y             the mouse at (X, Y), as winview's M
    MS B BUTTON DOWN X Y a button (0 l, 1 m, 2 r), as winview's B
    MS Q                 a quiet moment: what the adapter holds is one batch
    MS S PROGRAM         start a window M10 program (OURS harness below)
`--record F` writes a live session's events in this form, `replay` runs
one headless through the same Session.  A SCRIPT (wininput.py's input
script lines: type, key, shiftkey, ctrlkey, down, up, click, moveto,
wait; and `quiet`, `start PROGRAM`) compiles to it (`compile`).

PROGRAMS (`--program`, `start`): the HELD disc/exshow.esp etc. on the
Pmacs stand-ins, by test_espc.py Window's M10 harness (an as_program heir,
the substitute kanji_28 font entry, a menu item `M10`): OURS, as there.

Use:
    tools/winview/build.sh                    # once: SDL2 (brew install sdl2)
    python3 -I tools/simpos_live.py live [--start debugger|login|none]
            [--program exshow|cal|select] [--record F.events] [--scale N]
    python3 -I tools/simpos_live.py replay F.events OUT.pbm [--view SOCKET]
    python3 -I tools/simpos_live.py compile F.script OUT.events
    python3 -I tools/simpos_live.py shots F.script DIR   (screenshots, headless)
`live` starts the viewer itself (bsv/build-win/winview/winview, else
$WINVIEW), on a socket in a temporary directory.
"""
import os
import select
import socket
import struct
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PIM = os.path.dirname(HERE)
PSI = os.path.join(PIM, 'psi')
sys.path.insert(0, PSI)
sys.path.insert(0, HERE)

import kl0 as K  # noqa: E402
import espc  # noqa: E402
import fep_bridge as FB  # noqa: E402
import windev  # noqa: E402
import winfb  # noqa: E402
import wininput as W  # noqa: E402
import win_kl0_host as WH  # noqa: E402

FLUSH_MS = 40
POLL_S = 0.02
MAX_STEPS = 10 ** 12
WINVIEW = os.path.join(PIM, 'bsv', 'build-win', 'winview', 'winview')
ALT_USAGES = (0xe2, 0xe6)
# the starts (test_boot_route.py, fep_bridge.py): the system menu by the
# right button twice at fep_bridge.MENU_AT, then its item
DEBUGGER_ITEM_AT = (700, 589)
STARTS = {
    'debugger': ['click r %d %d' % FB.MENU_AT, 'click r %d %d' % FB.MENU_AT,
                 'click l %d %d' % DEBUGGER_ITEM_AT, 'quiet'],
    'login': ['click r %d %d' % FB.MENU_AT, 'click r %d %d' % FB.MENU_AT,
              'click l %d %d' % FB.LOGIN_ITEM_AT, 'quiet'],
    'none': [],
}


def say(msg):
    sys.stderr.write('simpos_live: %s\n' % msg)
    sys.stderr.flush()


# ------------------------------------------------------------ the input
class LiveAdapter(WH.Adapter):
    """win_kl0_host's Adapter (clicks, double clicks, moves) with the
    stand-ins' key codes (the module header) and full-width milliseconds
    (its 16-bit stamps could make two clicks 65 s apart a double)."""

    def _time(self, t):
        return t

    def record(self, kind, a, b, c, flags, t):
        if kind not in (1, 2, 3):
            return WH.Adapter.record(self, kind, a, b, c, flags, t)
        self._flush_click()
        self._flush_move()
        if kind == 1:
            code = a
            if flags & 1 and (0x2341 <= a <= 0x235a or 0x2361 <= a <= 0x237a):
                code = (a - 0x2340) & 0x1f          # control#"c": its ASCII control code
            self.out.append((t, ['key', code]))
        elif kind == 2:
            n = W.NAMES[a]
            self.out.append((t, ['key', espc.KEY_CODES[n]]))
        else:
            self.out.append((t, ['key', espc.PF_BASE + a]))


class Input:
    """Raw viewer events -> the coordinator's events (the module header)."""

    def __init__(self):
        self.kbd = W.KbdReceiver()
        self.ad = LiveAdapter()
        self.alt = set()
        self.held = {}          # a viewer button -> the PSI button it went down as
        self.errors = 0

    def key(self, down, usage, t):
        if usage in ALT_USAGES:
            (self.alt.add if down else self.alt.discard)(usage)
        if usage not in W.HOST and usage != W.PAUSE:
            say('key usage %02x is not in wininput.HOST: dropped' % usage)
            return
        for b in W.host_bytes(usage, down):
            for r in self.kbd.feed(b, 0):
                if r[0] == 6:
                    self.errors += 1
                    say('the keyboard receiver: error record %r' % (r,))
                    continue
                self.ad.record(*r, t)

    def move(self, x, y, t):
        self.ad.record(5, 0, x, y, 0, t)

    def button(self, b, down, x, y, t):
        if down:
            # OURS: Option + the left button is the middle button
            self.held[b] = 1 if (b == 0 and self.alt) else b
        pb = self.held.pop(b, b) if not down else self.held[b]
        self.ad.record(4, pb, x, y, 1 if down else 0, t)

    def quiet(self, t):
        """The adapter's events at a quiet moment T: [json event]."""
        self.ad.quiet(t)
        out = [e for _t, e in self.ad.out]
        self.ad.out = []
        return out

    def take(self, ev):
        """One parsed event line (ms, type, args)."""
        t, typ, a = ev
        if typ == 'K':
            self.key(a[0], a[1], t)
        elif typ == 'M':
            self.move(a[0], a[1], t)
        elif typ == 'B':
            self.button(a[0], a[1], a[2], a[3], t)


def parse_line(ln):
    w = ln.split('#', 1)[0].split()
    if not w:
        return None
    t, typ = int(w[0]), w[1]
    if typ == 'K':
        return (t, 'K', [int(w[2]), int(w[3], 16)])
    if typ in ('M', 'B'):
        return (t, typ, [int(v) for v in w[2:]])
    if typ == 'Q':
        return (t, 'Q', [])
    if typ == 'S':
        return (t, 'S', [w[2]])
    raise ValueError('an event line %r' % ln)


def fmt(ev):
    t, typ, a = ev
    if typ == 'K':
        return '%d K %d %02x' % (t, a[0], a[1])
    return ' '.join([str(t), typ] + [str(v) for v in a])


def compile_script(lines, t=0, pos=W.MOUSE0):
    """Script lines (the module header) -> event lines, and the end time."""
    out = []
    x, y = pos
    for ln in lines:
        w = ln.split('#', 1)[0].split() if not ln.lstrip().startswith('type ') else ln.split(None, 1)
        if not w:
            continue
        op = w[0]
        if op == 'quiet':
            t += 1000                       # longer than DCLICK_MS: a click is decided
            out.append((t, 'Q', []))
        elif op == 'start':
            t += 1
            out.append((t, 'S', [w[1]]))
        elif op == 'wait':
            t += int(w[1])
        elif op in ('moveto', 'click'):
            nx, ny = int(w[-2]), int(w[-1])
            if (nx, ny) != (x, y):
                t += 1
                out.append((t, 'M', [nx, ny]))
                x, y = nx, ny
            if op == 'click':
                b = W.BUTTONS[w[1]]
                for d in (1, 0):
                    t += 1
                    out.append((t, 'B', [b, d, x, y]))
        else:
            for p in W.expand(ln):
                if p[0] in ('kd', 'ku'):
                    t += 1
                    out.append((t, 'K', [1 if p[0] == 'kd' else 0, p[1]]))
                elif p[0] == 'w':
                    t += p[1]
                else:
                    raise ValueError('script line %r: %r' % (ln, p))
    return out, t, (x, y)


# ------------------------------------------------------------ the screen
def message(typ, payload):
    return typ.encode() + struct.pack('>I', len(payload)) + payload


def row_bytes(v):
    return v.to_bytes(winfb.W // 8, 'big')


class Screen:
    """The tee's frame and what of it has gone to the viewer.  SINK(bytes)
    takes the protocol's messages (a socket's sendall, or a Peer's)."""

    def __init__(self, sink, title='SIMPOS (kl0 stand-ins)'):
        self.frame = winfb.Frame(winfb.test_11())
        self.sink = sink
        self.title = title
        self.sent = None
        self.last = 0.0
        self.messages = 0

    def tee(self, op, args):
        self.frame.command(op, args)
        self.frame.reads = []
        if self.sink and time.monotonic() - self.last > FLUSH_MS / 1000.0:
            self.flush()

    def flush(self):
        self.last = time.monotonic()
        if not self.sink:
            return
        rows = self.frame.rows
        if self.sent is None:
            self.sink(message('H', struct.pack('>HH', winfb.W, winfb.H) + self.title.encode()))
            self.sink(message('F', struct.pack('>HH', winfb.W, winfb.H)
                              + b''.join(row_bytes(r) for r in rows)))
            self.messages += 2
            self.sent = list(rows)
            return
        ch = [j for j in range(winfb.H) if rows[j] != self.sent[j]]
        if not ch:
            return
        y0, y1 = ch[0], ch[-1] + 1
        self.sink(message('R', struct.pack('>HHHH', 0, y0, winfb.W, y1 - y0)
                          + b''.join(row_bytes(r) for r in rows[y0:y1])))
        self.messages += 1
        self.sent[y0:y1] = rows[y0:y1]

    def set_title(self, text):
        if self.sink:
            self.sink(message('T', text.encode()))


class Peer:
    """The viewer's side of the protocol in Python (OURS): the raster
    rebuilt from the H, F and R messages only, as winview.c's blit does,
    so a test hashes what the viewer was sent, not the device's frame."""

    def __init__(self):
        self.w = self.h = 0
        self.rows = []
        self.buf = b''
        self.counts = {}

    def __call__(self, data):
        self.buf += data
        while len(self.buf) >= 5:
            typ, n = chr(self.buf[0]), struct.unpack('>I', self.buf[1:5])[0]
            if len(self.buf) < 5 + n:
                return
            p, self.buf = self.buf[5:5 + n], self.buf[5 + n:]
            self.counts[typ] = self.counts.get(typ, 0) + 1
            if typ == 'H':
                self.w, self.h = struct.unpack('>HH', p[:4])
                self.rows = [0] * self.h
            elif typ == 'F':
                w, h = struct.unpack('>HH', p[:4])
                self.blit(0, 0, w, h, p[4:])
            elif typ == 'R':
                self.blit(*struct.unpack('>HHHH', p[:8]), p[8:])

    def blit(self, x, y, w, h, data):
        rb = (w + 7) // 8
        full = (1 << self.w) - 1
        for j in range(h):
            if not 0 <= y + j < self.h:
                continue
            v = int.from_bytes(data[j * rb:(j + 1) * rb], 'big') >> (rb * 8 - w)
            sh = self.w - x - w
            mask = ((1 << w) - 1) << sh if sh >= 0 else ((1 << w) - 1) >> -sh
            v = v << sh if sh >= 0 else v >> -sh
            self.rows[y + j] = (self.rows[y + j] & ~mask & full) | (v & mask & full)

    def pbm(self):
        nb = (self.w + 7) // 8
        return b'P4\n%d %d\n' % (self.w, self.h) + b''.join(r.to_bytes(nb, 'big') for r in self.rows)


# ------------------------------------------------------------ the session
def m10_window_harness():
    import test_espc as T
    return T, T.Window('test_win_m10_exshow')


class Session:
    """The stand-in SIMPOS on kl0 with its screen teed to SCREEN; NEXT()
    (the event source) is asked for a batch at every quiet moment and
    answers [json event], ('start', PROGRAM) or None (the end)."""

    def __init__(self, screen, programs=(), max_steps=MAX_STEPS):
        import held
        self.psi = psi = FB.PsiSide(max_steps=max_steps)
        psi.user, psi.shell = [], []
        self.m = m = psi.m
        self.T = self.t = None
        for prog in programs:
            T, t = self.harness()
            member, harness = T.Window.M10_HARNESS[prog]
            for src in (held.member_text(member), harness):
                ts, failed = espc.compile_text(src, 'simpos')
                if failed:
                    raise SystemExit('simpos_live: %s does not compile: %r' % (prog, failed))
                for c in ts:
                    m.lib.add(c)
        self.programs = set(programs)
        self.screen = screen
        self.dev = windev.device(m)
        self.dev.tees.append(screen.tee)
        self.batches = []

    def harness(self):
        if self.T is None:
            self.T, self.t = m10_window_harness()
        return self.T, self.t

    def run(self, next_batch):
        psi = self.psi

        def exchange(out):
            self.screen.flush()
            while not psi.shell:
                b = next_batch()
                if b is None:
                    return []
                if isinstance(b, tuple):
                    prog = b[1]
                    if prog not in self.programs:
                        raise SystemExit('simpos_live: start %s: give --program %s' % (prog, prog))
                    _T, t = self.harness()
                    evs = t.m10_start(self.m, prog, True)
                    self.batches.append(['start', prog])
                else:
                    if not b:
                        continue
                    evs = [FB.event(e) for e in b]
                    self.batches.append(b)
                psi.shell, psi.getl = evs, True
            return []
        stop = psi.run(exchange)
        self.screen.flush()
        return stop


def file_source(events, inp):
    """NEXT for a list of parsed event lines (replay)."""
    it = iter(events)

    def next_batch():
        for ev in it:
            t, typ, a = ev
            if typ == 'Q':
                return inp.quiet(t)
            if typ == 'S':
                return ('start', a[0])
            inp.take(ev)
        return None
    return next_batch


def replay(events, sink=None, programs=None):
    """Run parsed EVENTS headless through a Session.  -> (session, stop,
    the Input)."""
    if programs is None:
        programs = sorted({a[0] for _t, typ, a in events if typ == 'S'})
    inp = Input()
    sess = Session(Screen(sink), programs)
    stop = sess.run(file_source(events, inp))
    return sess, stop, inp


def read_events(path):
    out = []
    with open(path) as f:
        for ln in f:
            ev = parse_line(ln)
            if ev:
                out.append(ev)
    return out


def write_events(path, events, head=''):
    with open(path, 'w') as f:
        f.write('# tools/simpos_live.py events (OURS: the module header)\n' + head)
        for ev in events:
            f.write(fmt(ev) + '\n')


# ------------------------------------------------------------ live
class Viewer:
    """A connection to winview: sendall for the Screen, and the events it
    sends parsed.  Each event is stamped with the viewer's own time (the
    4-byte stamp K, M and B end with: when it was made, not when kl0 got
    to it), plus BASE; now() estimates the viewer's clock from the stamps
    seen (OURS)."""

    def __init__(self, path, base=0):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        for _ in range(200):
            try:
                self.s.connect(path)
                break
            except (FileNotFoundError, ConnectionRefusedError):
                time.sleep(0.05)
        else:
            raise SystemExit('simpos_live: no viewer at %s' % path)
        self.buf = b''
        self.base = base
        self.off = None         # the viewer's ms less ours, the largest seen
        self.last = base
        self.closed = False

    def mono(self):
        return int(time.monotonic() * 1000)

    def now(self):
        if self.off is None:
            return self.last
        return max(self.last, self.base + self.mono() + self.off)

    def stamp(self, p, at):
        if len(p) >= at + 4:
            v = struct.unpack('>I', p[at:at + 4])[0]
            off = v - self.mono()
            self.off = off if self.off is None else max(self.off, off)
            t = self.base + v
        else:
            t = self.now()          # an older viewer: no stamp
        self.last = max(self.last, t)
        return self.last

    def send(self, data):
        if not self.closed:
            try:
                self.s.sendall(data)
            except OSError:
                self.closed = True

    def poll(self, timeout):
        """-> [(ms, type, args)] that came within TIMEOUT seconds."""
        if self.closed:
            return [(self.now(), 'X', [])]
        r, _, _ = select.select([self.s], [], [], timeout)
        if r:
            try:
                got = self.s.recv(65536)
            except OSError:
                got = b''
            if not got:
                self.closed = True
                return [(self.now(), 'X', [])]
            self.buf += got
        out = []
        while len(self.buf) >= 5:
            typ, n = chr(self.buf[0]), struct.unpack('>I', self.buf[1:5])[0]
            if len(self.buf) < 5 + n:
                break
            p, self.buf = self.buf[5:5 + n], self.buf[5 + n:]
            if typ == 'K':
                out.append((self.stamp(p, 3), 'K', [p[0], struct.unpack('>H', p[1:3])[0]]))
            elif typ == 'M':
                out.append((self.stamp(p, 4), 'M', list(struct.unpack('>HH', p[:4]))))
            elif typ == 'B':
                b, d, x, y = struct.unpack('>BBHH', p[:6])
                out.append((self.stamp(p, 6), 'B', [b, d, x, y]))
            elif typ == 'Q':
                self.closed = True
                out.append((self.now(), 'X', []))
        return out


def live(argv):
    programs = [argv[i + 1] for i, a in enumerate(argv) if a == '--program']
    # a program's window over the debugger's two does not fit the save
    # memory (winfb BADSAVE): with --program the start is Login PIMOS
    start = argv[argv.index('--start') + 1] if '--start' in argv else ('login' if programs else 'debugger')
    if programs and start == 'debugger':
        raise SystemExit('simpos_live: --program with --start debugger does not fit the save memory '
                         '(winfb BADSAVE): use --start login or none')
    record = argv[argv.index('--record') + 1] if '--record' in argv else None
    scale = argv[argv.index('--scale') + 1] if '--scale' in argv else '1'
    viewer = os.environ.get('WINVIEW', WINVIEW)
    if not os.path.exists(viewer):
        raise SystemExit('simpos_live: no viewer at %s: run tools/winview/build.sh first' % viewer)
    if '--pre' in argv:
        # a script's events before the viewer's (simpos_live `shots`)
        with open(argv[argv.index('--pre') + 1]) as f:
            pre, t_end, _pos = compile_script(f.read().splitlines())
        start = 'pre'
    else:
        pre, t_end, _pos = compile_script(STARTS[start])
        for prog in programs:
            t_end += 1
            pre.append((t_end, 'S', [prog]))
    d = tempfile.mkdtemp(prefix='simpos_live')
    extra = [argv[i + 1] for i, a in enumerate(argv) if a == '--viewer-arg']
    vp = subprocess.Popen([viewer, 'v.sock', '--scale', scale] + extra, cwd=d)
    cwd = os.getcwd()
    os.chdir(d)                         # the socket's path is short (sun_path)
    try:
        v = Viewer('v.sock', t_end + 1)
    finally:
        os.chdir(cwd)
    taken = list(pre)       # the session's events so far, all of them taken well
    head = '# a live session (--start %s%s)\n' % (start, ''.join(' --program ' + p for p in programs))
    try:
        sessions(v, taken, programs)
    finally:
        if record:
            write_events(record, taken, head)
            say('recorded %d events in %s' % (len(taken), record))
        if vp.poll() is None:
            vp.terminate()
        vp.wait()
        import shutil
        shutil.rmtree(d, ignore_errors=True)
    return 0


def sessions(v, taken, programs):
    """Run the session on viewer V until it closes.  A refusal (a menu
    item whose class is not stood in, a goal the stand-ins refuse) takes
    back the batch that met it: the session runs again from the boot
    without it (OURS).  TAKEN: the events so far, all of them taken well.
    -> the number of take-backs."""
    backs = 0
    while True:
        stop, sess, screen, failed_from = live_run(v, taken, programs)
        if stop is None or v.closed or stop.cause == 'would suspend':
            return backs
        msg = '%s: %s' % (stop.cause, stop.detail)
        say('the PSI refused: %s' % msg)
        say('  at %s' % ' < '.join(sess.psi.where(6)))
        if failed_from is None:
            say('the refusal came while replaying events that ran before: stopping')
            screen.set_title('SIMPOS STOPPED: ' + msg[:100])
            while not v.closed:
                v.poll(0.2)
            return backs
        del taken[failed_from:]
        backs += 1
        say('taking back the last batch of events: the session runs again without it')
        v.send(message('T', ('SIMPOS: refused (%s) - taken back' % msg[:80]).encode()))


def live_run(v, taken, programs):
    """One run of the session: TAKEN replayed (the screen held), then the
    viewer's events, appended to TAKEN as they are taken.  -> (the stop,
    the session, its screen, the index in TAKEN of the batch the stop met,
    None if it met a replayed one)."""
    inp = Input()
    screen = Screen(None)
    say('booting the stand-in SIMPOS (kl0)%s...' % (', replaying %d events' % len(taken) if taken else ''))
    sess = Session(screen, programs)
    replayed = file_source(list(taken), inp)
    st = dict(replay=True, start=len(taken), last=None)

    def next_batch():
        if st['replay']:
            b = replayed()
            if b is not None:
                return b
            st['replay'] = False
            screen.sink = v.send
            screen.flush()
            v.send(message('T', b'SIMPOS (kl0 stand-ins)'))
        while True:
            for ev in v.poll(POLL_S):
                if ev[1] == 'X':
                    # the viewer closed: what the adapter holds goes in
                    # first (a click not yet decided, a held move)
                    inp.ad.quiet(final=True)
                    out = [e for _t, e in inp.ad.out]
                    inp.ad.out = []
                    if out:
                        st['last'] = st['start']
                        taken.append((ev[0], 'Q', []))
                        st['start'] = len(taken)
                        return out
                    return None
                taken.append(ev)
                inp.take(ev)
            now = v.now()
            out = inp.quiet(now)
            if out:
                st['last'] = st['start']
                taken.append((now, 'Q', []))
                st['start'] = len(taken)
                return out
    stop = sess.run(next_batch)
    if st['replay'] and screen.sink is None:
        screen.sink = v.send
        screen.flush()
    return stop, sess, screen, st['last']


def shots(script, out):
    """Each `# stage NAME` of SCRIPT: its events up to the mark run
    headless through `live` and the real viewer (SDL's dummy driver; the
    events up to the script's last `start` given as --pre, the rest
    pushed by winview's --events), and winview's own --dump of its last
    frame, checked against an in-process replay of the same events, is
    written as OUT/live_NAME.png."""
    import hashlib
    import shutil
    with open(script) as f:
        lines = f.read().splitlines()
    starts = [i for i, ln in enumerate(lines) if ln.split()[:1] == ['start']]
    cut = starts[-1] + 1 if starts else 0
    programs = sorted({lines[i].split()[1] for i in starts})
    d = tempfile.mkdtemp(prefix='simpos_shots')
    try:
        pre = os.path.join(d, 'pre.script')
        with open(pre, 'w') as f:
            f.write('\n'.join(lines[:cut]) + '\n')
        for i, ln in enumerate(lines):
            if not ln.startswith('# stage ') or i < cut:
                continue
            name = ln.split()[2]
            pe, t, _p = compile_script(lines[:cut])
            ev, _t, _p = compile_script(lines[cut:i], t)
            evf, dump = os.path.join(d, name + '.events'), os.path.join(d, name + '.pbm')
            write_events(evf, ev)
            cmd = [sys.executable, '-I', os.path.abspath(__file__), 'live', '--pre', pre]
            for prog in programs:
                cmd += ['--program', prog]
            for a in ('--events', evf, '--dump', dump, '--linger', '10000'):
                cmd += ['--viewer-arg', a]
            r = subprocess.run(cmd, env=dict(os.environ, SDL_VIDEODRIVER='dummy'),
                               capture_output=True, text=True)
            if r.returncode or not os.path.exists(dump) or 'refused' in r.stderr:
                raise SystemExit('simpos_live shots: %s failed:\n%s' % (name, r.stderr[-2000:]))
            with open(dump, 'rb') as f:
                got = f.read()
            peer = Peer()
            replay(pe + ev, peer)
            if got != peer.pbm():
                raise SystemExit('simpos_live shots: %s: the viewer\'s dump is not the replay\'s frame' % name)
            fr = winfb.Frame()
            fr.rows = list(peer.rows)
            path = os.path.join(out, 'live_%s.png' % name)
            with open(path, 'wb') as f:
                f.write(windev.png_bytes(fr))
            print(path, hashlib.sha256(got).hexdigest())
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return 0


def main(argv):
    if argv[:1] == ['live']:
        return live(argv[1:])
    if argv[:1] == ['shots'] and len(argv) == 3:
        return shots(argv[1], argv[2])
    if argv[:1] == ['compile'] and len(argv) == 3:
        with open(argv[1]) as f:
            evs, _t, _p = compile_script(f.read().splitlines())
        write_events(argv[2], evs, '# compiled from %s\n' % os.path.basename(argv[1]))
        return 0
    if argv[:1] == ['replay'] and len(argv) >= 3:
        events = read_events(argv[1])
        sink = None
        v = None
        if '--view' in argv:
            v = Viewer(argv[argv.index('--view') + 1])
            sink = v.send
        peer = Peer()

        def both(data):
            peer(data)
            if sink:
                sink(data)
        sess, stop, inp = replay(events, both)
        with open(argv[2], 'wb') as f:
            f.write(peer.pbm())
        same = peer.pbm() == sess.dev.frame.pbm()
        print('stop: %s' % ('%s: %s' % (stop.cause, stop.detail) if stop else None))
        print('batches: %d; messages: %r; input errors: %d' % (len(sess.batches), peer.counts, inp.errors))
        print('viewer frame sha256 %s, %d dots; = the device frame: %s'
              % (windev.pbm_sha256(sess.dev.frame) if same else
                 __import__('hashlib').sha256(peer.pbm()).hexdigest(),
                 sum(bin(r).count('1') for r in peer.rows), same))
        return 0 if same else 1
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
