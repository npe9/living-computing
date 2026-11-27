#!/usr/bin/env python3
"""Window M11's live view (2026-11-26, OURS): the stand-in SIMPOS driving
tools/winview, run headless (tools/simpos_live.py).

    python3 -I psi/test_live.py          (~40 s; the winview leg needs sdl2)

The recorded mode: a session's events (psi/live_sessions/*.script, a
user's keys and mouse at the viewer, compiled to the viewer's raw events
and written to an event file and read back) run through simpos_live's
Session, the live launcher's own path: the viewer's events -> wininput.py's
tables -> the adapter -> the coordinator's events, given at quiet moments
as the scripted tests' are; the device's commands teed to simpos_live's
frame and sent as the protocol's H, F and R messages.  The frame checked is
the one REBUILT FROM THOSE MESSAGES (simpos_live.Peer, as winview.c blits
them), and it must equal the scripted tests' pins:

  - test_live_pins:
      debugger_dialogue  test_boot_route.py SCREEN_SHA (shifted punctuation,
                         RETURN, the system menu by mouse#rr)
      debugger_rubout    the same dots, typed with mistakes taken back by
                         Backspace and Delete (getl/2's rubout, window M11,
                         OURS), across the debugger's wrapped line and in
                         the unechoed password
      system_menu        test_espc.py Window MENU_PINS['boxed']
      pmacs_editor       Window M10_PINS['pmacs'] (Ctrl letters as control
                         codes: C-n, C-x C-s; the M10 harness's `start`)
      manipulator_reshape  Window SHOT_PINS['reshaped'] (the middle button,
                         left clicks 500 ms apart, a move between batches)
      manipulator_hide   Window SHOT_PINS['hidden'] (HIDE: the save area
                         restored)
      editor_menu        Window M10_PINS['editor_menu'] (one right click,
                         mouse#r after the double-click time, not rr)
    and the frame the viewer was sent = the device's frame.
  - test_live_keys: the viewer's raw events -> the coordinator's events, by
    the tables: the named keys (espc.KEY_CODES), pf#, Ctrl, Shift,
    Option+left = middle (OURS), double clicks within 400 ms, and two
    clicks 500 ms apart staying single.
  - test_live_takeback: the live loop (simpos_live.sessions) on a stand-in
    viewer: a click on the system menu's `pmacs` (no stand-in class: a
    refusal) is taken back by running the session again without its
    batch; the line typed next reaches the debugger, and the events kept
    replay to the frame the viewer was last sent.
  - test_live_winview: (only if pkg-config finds sdl2) the real viewer,
    built from tools/winview, headless (SDL_VIDEODRIVER=dummy): its
    --events pushes debugger_dialogue's events into SDL's own queue, so
    they leave through winview's event code with its time stamps; the live
    launcher (`live --start none`) takes them as a user's; the viewer's own
    --dump of its last frame = SCREEN_SHA, and the launcher's --record of
    the session replays to it.

Injections, OBSERVED (2026-11-26, each into the file itself, restored with
cp and checked with cmp; this file run; the subtests named by session):
  I1 tools/wininput.py key_event: Shift lost on digits and punctuation (a
     wrong key mapping; the script compiler, which uses only the tables, is
     unaffected): test_live_keys FAIL, test_live_pins FAIL
     (debugger_dialogue, debugger_rubout), test_live_winview FAIL.
  I2 psi/windev.py Device.run: the tee skips the glyph command (a dropped
     tee command): test_live_pins FAIL (all five sessions: the viewer's
     frame differs from the pin), test_live_winview FAIL; _keys OK.
  I3 tools/simpos_live.py LiveAdapter: Ctrl with a letter sends the JIS
     code (win_kl0_host's Adapter's way): test_live_keys FAIL,
     test_live_pins FAIL (pmacs_editor); _winview OK.
  I4 psi/standin/standard_io_window.esp: BS and DEL kept in the line (no
     rubout): test_live_pins FAIL (debugger_rubout) only.
  I5 tools/simpos_live.py Screen.flush: the changed band sent one row
     short: test_live_pins FAIL (all five), test_live_winview FAIL; _keys
     OK.
  I6 tools/simpos_live.py sessions: the take-back drops one event more
     (the quiet mark before the refused batch): test_live_takeback FAIL
     only.
(I1-I5 were run before test_live_takeback existed, I6 after it; all six
before manipulator_hide and editor_menu joined test_live_pins.)
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(HERE, '..', 'tools')
sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)

import espc  # noqa: E402
import simpos_live as L  # noqa: E402
import test_boot_route as BR  # noqa: E402
import test_espc as T  # noqa: E402

SESSIONS = os.path.join(HERE, 'live_sessions')


def pins():
    W = T.Window
    return {'debugger_dialogue': (BR.SCREEN_SHA, None),
            'debugger_rubout': (BR.SCREEN_SHA, None),
            'system_menu': W.MENU_PINS['boxed'],
            'pmacs_editor': W.M10_PINS['pmacs'],
            'manipulator_reshape': W.SHOT_PINS['reshaped'],
            'manipulator_hide': W.SHOT_PINS['hidden'],
            'editor_menu': W.M10_PINS['editor_menu']}


def compiled(name, path):
    with open(os.path.join(SESSIONS, name + '.script')) as f:
        evs, _t, _p = L.compile_script(f.read().splitlines())
    L.write_events(path, evs)
    return L.read_events(path)


def K_codes(text):
    import kl0
    return kl0.Str(text).codes()


def dots(rows):
    return sum(bin(r).count('1') for r in rows)


class Live(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='test_live')

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_live_pins(self):
        for name, (sha, n) in sorted(pins().items()):
            with self.subTest(session=name):
                self.pinned(name, sha, n)

    def pinned(self, name, sha, n):
        events = compiled(name, os.path.join(self.tmp, name + '.events'))
        peer = L.Peer()
        sess, stop, inp = L.replay(events, peer)
        self.assertEqual(stop.cause, 'would suspend', name)
        self.assertEqual(inp.errors, 0, name)
        got = peer.pbm()
        self.assertEqual(hashlib.sha256(got).hexdigest(), sha, name)
        if n is not None:
            self.assertEqual(dots(peer.rows), n, name)
        self.assertEqual(got, sess.dev.frame.pbm(), name)
        self.assertGreater(peer.counts.get('R', 0), 0, name)

    def keys(self, lines):
        evs, t, _p = L.compile_script(lines + ['quiet'])
        inp = L.Input()
        out = []
        nb = L.file_source(evs, inp)
        while True:
            b = nb()
            if b is None:
                return out
            out += b

    def test_live_keys(self):
        K = espc.KEY_CODES
        J = L.W.jis
        self.assertEqual(self.keys(['type a:Z)']), [['key', J(c)] for c in 'a:Z)'])
        self.assertEqual(self.keys(['key enter', 'key kpenter', 'key bs', 'key del', 'key tab', 'key esc',
                                    'key up', 'key down', 'key left', 'key right', 'key insert',
                                    'key pause']),
                         [['key', K[n]] for n in ('cr', 'enter', 'bs', 'del', 'tab', 'esc', 'up', 'down',
                                                  'left', 'right', 'help', 'abort')])
        self.assertEqual(self.keys(['key f1', 'key f12', 'shiftkey f1', 'shiftkey f7', 'shiftkey f8']),
                         [['key', espc.PF_BASE + n] for n in (0, 11, 12, 18, 7)])
        self.assertEqual(self.keys(['ctrlkey x', 'ctrlkey s', 'ctrlkey n', 'ctrlkey a', 'ctrlkey j',
                                    'ctrlkey g', 'ctrlkey 1', 'altkey q']),
                         [['key', c] for c in (24, 19, 14, 1, 10, 7, J('1'), J('q'))])
        self.assertEqual(self.keys(['click r 640 560', 'click r 640 560', 'click l 10 20', 'wait 500',
                                    'click l 30 40', 'down alt', 'click l 50 60', 'up alt', 'wait 500', 'click m 1 2',
                                    'click m 1 2', 'moveto 7 8']),
                         [['mouse', 'rr', 640, 560], ['mouse', 'l', 10, 20], ['mouse', 'l', 30, 40],
                          ['mouse', 'm', 50, 60], ['mouse', 'mm', 1, 2], ['move', 7, 8]])
        # a move is held until the quiet moment, or dropped by a click
        self.assertEqual(self.keys(['moveto 5 5', 'moveto 6 6', 'click l 9 9']), [['mouse', 'l', 9, 9]])

    def test_live_takeback(self):
        # the live loop (simpos_live.sessions) on a stand-in viewer: the
        # system menu's `pmacs` (its class not stood in: a refusal) is
        # taken back, the session runs again without that batch, and the
        # line typed next reaches the debugger; the events kept replay to
        # the frame the viewer was last sent
        class FakeViewer:
            def __init__(self, groups):
                self.groups, self.closed, self.t = list(groups), False, 10 ** 6
                self.peer = L.Peer()

            def send(self, data):
                self.peer(data)

            def now(self):
                return self.t + 1000

            def poll(self, timeout):
                if not self.groups:
                    self.closed = True
                    return [(self.now(), 'X', [])]
                g = self.groups.pop(0)
                self.t = g[-1][0]
                return g

        def group(lines, t):
            evs, t, _p = L.compile_script(lines, t)
            return evs, t + 1000
        pre, t, _p = L.compile_script(L.STARTS['debugger'])
        menu, t = group(['click r 640 560', 'click r 640 560', 'click l 700 605'], t + 1000)
        line, t = group(['type :create(#process,P).', 'key enter'], t)
        v = FakeViewer([menu, line])
        taken = list(pre)
        self.assertEqual(L.sessions(v, taken, []), 1)
        self.assertEqual([e for e in taken if e[1] != 'Q'], pre[:-1] + line)
        peer = L.Peer()
        sess, stop, inp = L.replay(taken, peer)
        self.assertEqual(peer.pbm(), v.peer.pbm())
        self.assertEqual([b for b in sess.batches if any(e[0] == 'key' for e in b)],
                         [[['key', c] for c in K_codes(':create(#process,P).') + [13]]])

    def test_live_winview(self):
        if subprocess.run(['pkg-config', '--exists', 'sdl2']).returncode != 0:
            self.skipTest('pkg-config finds no sdl2: the winview leg is not run')
        viewer = os.path.join(self.tmp, 'winview')
        r = subprocess.run([os.path.join(TOOLS, 'winview', 'build.sh'), viewer],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        events = os.path.join(self.tmp, 'd.events')
        compiled('debugger_dialogue', events)
        dump, rec = os.path.join(self.tmp, 'dump.pbm'), os.path.join(self.tmp, 'd.rec')
        env = dict(os.environ, SDL_VIDEODRIVER='dummy', WINVIEW=viewer)
        r = subprocess.run([sys.executable, '-I', os.path.join(TOOLS, 'simpos_live.py'), 'live',
                            '--start', 'none', '--viewer-arg', '--events', '--viewer-arg', events,
                            '--viewer-arg', '--dump', '--viewer-arg', dump, '--viewer-arg', '--linger',
                            '--viewer-arg', '10000', '--record', rec],
                           env=env, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        self.assertNotIn('refused', r.stderr)
        with open(dump, 'rb') as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), BR.SCREEN_SHA)
        peer = L.Peer()
        sess, stop, inp = L.replay(L.read_events(rec), peer)
        self.assertEqual(hashlib.sha256(peer.pbm()).hexdigest(), BR.SCREEN_SHA)


if __name__ == '__main__':
    unittest.main()
