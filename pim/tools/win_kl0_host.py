#!/usr/bin/env python3
"""The kl0 host for the window hardware's Bluesim runs (H7s, OURS).

docs/simpos/window_hardware_plan.md H7s and §4.1.  With option (a) the
board is the display and the keyboard, and the host runs kl0: the input
box's event records come up the link, the host turns them into the
coordinator stand-in's events (psi/standin/coordinator.esp: {key, Code},
{mouse, Button, X, Y}, {move, X, Y}), runs kl0, and sends the drawing
down.  bsv/WinHostDev.c runs this file as its child (WIN_KL0_HOST) and
speaks its line protocol (that file's header):
    in:  E KIND A B C FLAGS T  (hex)   an event record
         Q T                           input quiet; F T  the script is done
         X                             the end
    out: D HEX...                      link frames' bytes;  .  the answer's end
         X MESSAGE                     a failure (the run stops)

THE ADAPTER from raw records to the coordinator's events (ALL OURS; the
plan §3.2 leaves double clicks to the handler process, whose stand-in
does not classify them, so it is done here, and is an open item for
psi/; tools/simpos_live.py, the software stack's live view, uses this
Adapter's click and move rules too, with its own key codes):
  - a key with a JIS code -> {key, JIS}; named keys -> {key, Code} with
    their ASCII control codes, cr and keypad enter 13, lf 10, tab 9, bs 8,
    del 127, esc 27, bell 7 (OURS: only RETURN, 13, is used by the held
    requester, psi/test_espc.py Standins.keys); arrows, help, abort and
    pf# keys have no stand-in handler: reported on stderr and dropped;
  - a button down then up is a click at the down's position; a second
    click of the same button whose down comes within DCLICK_MS of the
    first's up makes a double click (mouse#ll, mm, rr), else the first is
    a single (mouse#l, m, r), decided by the next record or the quiet
    time;
  - moves are held: consecutive moves keep the last; a held move is
    dropped when the next record is a button down (the click carries the
    position), else sent as {move, X, Y} before it or at the quiet time;
  - error records are reported on stderr and counted.

TWO ROUTES:
  --tape PATH   psi/fep_bridge.py's replay route (window M4): the events,
                split into batches where the records' time stamps leave a
                gap of BATCH_MS, must equal the tape's script (its `login`
                and `shell` batches); at F the PSI side runs with that
                script against the tape's PIMOS exchanges, and its device
                log is sent down.  So the run's oracle is the tape, and the
                frame's the test's pin.
  --probe       step 3m's route (test_espc.py Window.screen: boot_to_top
                with the B3M probes standing in for PIMOS): at every Q and
                F, kl0 runs again from the boot with all the events so far,
                and the part of its device log not yet sent goes down (the
                logs of a longer input extend the shorter's, which is
                checked; if not, the frame is cleared and the whole log
                sent, with a message).  Interactive runs use this route.
--report FILE   at F, the verdicts: the script (JSON), `script = tape`,
                the software frame's sha256 and dots, the pin's (tape
                route), and the commands sent.

Also:  python3 -I tools/win_kl0_host.py expect SCRIPT the events a script must give (JSON)
       python3 -I tools/win_kl0_host.py mode N        the monitor's mode line
       python3 -I tools/win_kl0_host.py config N OUT  win_scan.hex, cursor off
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PSI = os.path.join(HERE, '..', 'psi')
sys.path.insert(0, PSI)
sys.path.insert(0, HERE)

DCLICK_MS = 400
BATCH_MS = 1000
NAMES = ['lf', 'cr', 'del', 'enter', 'esc', 'tab', 'bs', 'bell', 'up', 'down', 'left', 'right',
         'abort', 'help']
NAMED_CODE = {'cr': 13, 'enter': 13, 'lf': 10, 'tab': 9, 'bs': 8, 'del': 127, 'esc': 27,
              'bell': 7}
BTN = 'lmr'


def log(msg):
    sys.stderr.write('win_kl0_host: %s\n' % msg)
    sys.stderr.flush()


class Adapter:
    """Raw event records -> [(t, json event)], OURS (the module header)."""

    def __init__(self):
        self.out = []           # [(t, event)]
        self.move = None        # (t, x, y) held
        self.down = {}          # button -> (t, x, y)
        self.click = None       # (button, t_up, x, y): a single click not yet decided
        self.errors = 0
        self.t_hi = 0
        self.t_last = None

    def _time(self, t16):
        if self.t_last is not None and t16 < self.t_last:
            self.t_hi += 1 << 16
        self.t_last = t16
        return self.t_hi + t16

    def _flush_move(self):
        if self.move:
            t, x, y = self.move
            self.out.append((t, ['move', x, y]))
            self.move = None

    def _flush_click(self, now=None):
        if self.click and (now is None or now - self.click[1] > DCLICK_MS):
            b, t, x, y = self.click
            self.out.append((t, ['mouse', b, x, y]))
            self.click = None

    def record(self, kind, a, b, c, flags, t16):
        t = self._time(t16)
        if kind == 5:
            self.move = (t, b, c)
            return
        if kind == 4:
            name = BTN[a]
            if flags & 1:
                self.move = None                        # the click carries the place
                if self.click and (self.click[0] != name or t - self.click[1] > DCLICK_MS):
                    self._flush_click()
                self.down[name] = (t, b, c)
                return
            t0, x, y = self.down.pop(name, (t, b, c))
            if self.click and self.click[0] == name:
                self.out.append((self.click[1], ['mouse', name + name, self.click[2], self.click[3]]))
                self.click = None
            else:
                self.click = (name, t, x, y)
            return
        self._flush_click()
        self._flush_move()
        if kind == 1:
            if flags:
                log('a key with Ctrl/Alt (%04x, flags %d): sent as its code' % (a, flags))
            self.out.append((t, ['key', a]))
        elif kind == 2:
            n = NAMES[a] if a < len(NAMES) else '?%d' % a
            if n in NAMED_CODE:
                self.out.append((t, ['key', NAMED_CODE[n]]))
            else:
                log('key#%s has no stand-in handler: dropped' % n)
        elif kind == 3:
            log('pf#%d has no stand-in handler: dropped' % a)
        else:
            self.errors += 1
            log('an input error record: code %d (b %04x, flags %02x)' % (a, b, flags))

    def quiet(self, now16=None, final=False):
        now = None if final else (self._time(now16) if now16 is not None else None)
        self._flush_click(None if final else now)
        if final or self.click is None:
            self._flush_move()


def batches(evs):
    out = []
    last = None
    for t, e in evs:
        if last is None or t - last >= BATCH_MS:
            out.append([])
        out[-1].append(e)
        last = t
    return out


# ------------------------------------------------------------ the routes
class Sender:
    def __init__(self):
        self.seq = 0
        self.sent = []          # the device log already sent

    def frames(self, cmds):
        import winlink
        out = []
        for op, a in cmds:
            out += winlink.frame(self.seq, winlink.record_bytes(op, a))
            self.seq = (self.seq + 1) & 0xff
        return out

    def send(self, log_):
        import winfb
        n = len(self.sent)
        if log_[:n] != self.sent:
            log('the new log does not extend the one sent: the frame is cleared and all of it sent')
            cmds = [((winfb.FILL << 4) | 1, [0, 0, 1280, 1024, 0, 0])] + list(log_)
        else:
            cmds = log_[n:]
        self.sent = list(log_)
        data = self.frames(cmds)
        for k in range(0, len(data), 1800):
            print('D ' + ''.join('%02x' % b for b in data[k:k + 1800]))
        return len(cmds)


def window():
    import test_espc as T
    T.Window.setUpClass()
    return T, T.Window('test_win_m5_login_screen')


def probe_run(t, evs):
    import fep_bridge as FB
    import windev
    m, r = t.boot_to_top([FB.event(e) for e in evs], probes=t.B3M_PROBES, boot='b3m_boot',
                         before=t.pimos_texts(t.PIMOS_OK))
    return windev.device(m)


def tape_run(path, script):
    import fep_bridge as FB
    import windev
    with open(path) as f:
        tp = json.load(f)
    psi = FB.PsiSide(script=script)
    tape = list(tp['exchanges'])

    def exchange(from_psi):
        if not tape:
            raise AssertionError('the PSI asks for an exchange the tape does not have')
        e = tape.pop(0)
        if [r.hex() for r in from_psi] != e['from_psi']:
            raise AssertionError('the PSI sent other bytes than the tape has')
        return [bytes.fromhex(r) for r in e['to_psi']]
    stop = psi.run(exchange)
    return windev.device(psi.m), stop, tape, tp


def serve(argv):
    tape = argv[argv.index('--tape') + 1] if '--tape' in argv else None
    report = argv[argv.index('--report') + 1] if '--report' in argv else None
    ad = Adapter()
    snd = Sender()
    T = t = None
    rep = {}
    for line in sys.stdin:
        w = line.split()
        if not w:
            continue
        if w[0] == 'E':
            try:
                ad.record(int(w[1]), *[int(v, 16) for v in w[2:7]])
            except (IndexError, ValueError) as e:
                ad.errors += 1
                log('a record the adapter cannot read: %r (%s)' % (line.strip(), e))
            continue
        if w[0] == 'X':
            break
        final = w[0] == 'F'
        # the quiet time (WinHostDev.c's WIN_QUIET_MS, 500 by default) is
        # longer than DCLICK_MS, so a held click or move is decided now
        ad.quiet(final=True)
        try:
            if tape and final:
                script = batches(ad.out)
                tp = json.load(open(tape))
                want = tp['script']
                got = dict(login=script[0] if script else [], shell=script[1] if len(script) > 1 else [])
                rep['script'] = got
                rep['batches'] = len(script)
                rep['script_equals_tape'] = got == want and len(script) <= 2
                if not rep['script_equals_tape']:
                    log('the script from the receivers is not the tape\'s: %r' % (got,))
                    print('X the script from the receivers is not the tape\'s')
                else:
                    import windev
                    if T is None:
                        T, t = window()
                    dev, stop, left, _tp = tape_run(tape, got)
                    rep['stop'] = stop.cause if stop else None
                    rep['exchanges_left'] = len(left)
                    rep['sw_sha'] = windev.pbm_sha256(dev.frame)
                    rep['sw_dots'] = dev.frame.count()
                    if os.path.basename(tape) == 'console_pwd.json':
                        rep['pin'] = list(T.Window.CONSOLE_PIN)
                    rep['commands'] = snd.send(dev.log)
            elif not tape and (final or ad.out or not snd.sent):
                import windev
                if T is None:
                    T, t = window()
                dev = probe_run(t, [e for _t, e in ad.out])
                rep['script'] = [e for _t, e in ad.out]
                rep['sw_sha'] = windev.pbm_sha256(dev.frame)
                rep['sw_dots'] = dev.frame.count()
                rep['commands'] = snd.send(dev.log)
        except Exception as e:          # a kl0 failure ends the run loudly
            log('kl0: %s: %s' % (type(e).__name__, e))
            print('X kl0 failed: %s' % type(e).__name__)
        print('.')
        sys.stdout.flush()
        if report:
            rep['input_errors'] = ad.errors
            with open(report, 'w') as f:
                json.dump(rep, f, indent=1)
    return 0


def expect(path):
    """The coordinator events a high-level input script must give, by
    tools/wininput.py's models (its HOST table and receivers) and this
    adapter, independently of the RTL and of WinHostDev.c: the actions in
    order, each record stamped with the script's waits so far (ms)."""
    import wininput as W
    prims = W.expand(open(path).read())
    ad = Adapter()
    kb, ms = [], []
    nk = nm = 0
    t = 0
    for p in prims:
        if p[0] == 'w':
            t += p[1]
            continue
        k, m = W.device_bytes([p])
        kb += [(b, f) for b, f, _w in k]
        ms += [(b, f) for b, f, _w in m]
        rk, rm = W.receive_kbd(kb), W.receive_mouse(ms)
        for r in rk[nk:] + rm[nm:]:
            ad.record(*r, t & 0xffff)
        nk, nm = len(rk), len(rm)
        t += 1
    ad.quiet(final=True)
    return [e for _t, e in ad.out]


def mode_line(n):
    import winscan
    m = winscan.MODES[n]
    return ' '.join(str(int(m[k])) for k in ('ha', 'hf', 'hs', 'hb', 'va', 'vf', 'vs', 'vb',
                                             'hpos', 'vpos', 'x0', 'y0', 'fw', 'fh', 'half'))


def config(n, out):
    import winscan
    w = winscan.config_words('mode%d' % n)
    w[16] = 0                            # the cursor off: the software frame has none
    with open(out, 'w') as f:
        f.write(''.join('%08x\n' % v for v in w))


def main(argv):
    if argv[:1] == ['mode'] and len(argv) == 2:
        print(mode_line(int(argv[1])))
        return 0
    if argv[:1] == ['config'] and len(argv) == 3:
        config(int(argv[1]), argv[2])
        return 0
    if argv[:1] == ['expect'] and len(argv) == 2:
        print(json.dumps(expect(argv[1])))
        return 0
    if argv[:1] == ['run']:
        return serve(argv[1:])
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
