#!/usr/bin/env python3
"""kl0's window drawing through the host link RTL (window hardware H6).

docs/simpos/window_hardware_plan.md H6: "the M1/M4 runs of
psi/test_espc.py drive Bluesim through a pipe with equal PBM hashes".
This is the bench equivalent of the device layer's tee mode (which lives
in psi/ and belongs to the window software's owner: an open item there).
A live kl0 run's device log IS a winfb command stream (psi/windev.py
Device.log), so the run is made here, in the test's own way, and its log
is framed by tools/winlink.py and sent down mkWinLink's line in
bsv/WinLinkTb.bsv.  ALL OURS.

THE RUNS (read only: psi/test_espc.py's helpers, its pins imported at run
time, never copied):
  m1  window M1/M5: boot, the system menu, Login PIMOS and the keys of
      Window.SCREENS 'name', 'password', 'login' (the held requester's
      three prompts, the echo-less password).  The three stages' logs are
      prefixes of one another (checked here: the run fails loud if not),
      so ONE stream is sent: the 'login' log with a dump after the 'name'
      prefix, one after the 'password' prefix, and one at its end.
  m4  window M4: PIMOS's console bridged to the PSI (fep_bridge replay of
      psi/fep_bridge_tapes/console_pwd.json): the system menu by the
      mouse, Login PIMOS, `Shell>> `, `pwd` and PIMOS's answer; one dump
      at the end.
Each dump's sha256 must equal the test's pin for that stage (PINS[stage],
CONSOLE_PIN), and the dump read back over the link must equal it too:
`pins` checks the second, run_win_link.sh's `winlink.py check` the
statuses, the error records and every dump against psi/winfb.py.

The per-event-step comparison of the plan is made at the stage boundaries
only: one dump is 1,280 data records up the link (about 171 kB, about
6.8 M bench cycles at 4 cycles a bit), so a dump per command would cost
hours of Bluesim.

Use:
    python3 -I tools/win_kl0_link.py streams OUTDIR    # m1.stream m4.stream m1.pins m4.pins
    python3 -I tools/win_kl0_link.py pins OUT.hex PINS  # the up bytes' dumps against PINS
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PSI = os.path.join(HERE, '..', 'psi')
sys.path.insert(0, PSI)
sys.path.insert(0, HERE)


def kl0_logs():
    """{case: (log [(op, a)], [(dump after n commands, stage, pin sha)])}"""
    import test_espc as T
    import windev
    T.Window.setUpClass()
    t = T.Window('test_win_m5_login_screen')
    logs = {}
    for st in ('name', 'password', 'login'):
        _m, _p, _w, dev = t.screen(T.Window.SCREENS[st][0])
        logs[st] = list(dev.log)
        if windev.pbm_sha256(dev.frame) != T.Window.PINS[st][0]:
            raise SystemExit('win_kl0_link: the %s run is not its pin' % st)
    for a, b in (('name', 'password'), ('password', 'login')):
        if logs[b][:len(logs[a])] != logs[a]:
            raise SystemExit('win_kl0_link: the %s log is not a prefix of the %s log' % (a, b))
    out = {'m1': (logs['login'], [(len(logs[s]), s, T.Window.PINS[s][0])
                                  for s in ('name', 'password', 'login')])}
    psi, _tape = t.console()
    dev = windev.device(psi.m)
    if windev.pbm_sha256(dev.frame) != T.Window.CONSOLE_PIN[0]:
        raise SystemExit('win_kl0_link: the console run is not its pin')
    out['m4'] = (list(dev.log), [(len(dev.log), 'console', T.Window.CONSOLE_PIN[0])])
    return out


def stream_of(log, dumps):
    import winfb
    at = {n for n, _s, _p in dumps}
    lines = []
    for k, (op, a) in enumerate(log, 1):
        lines.append(winfb.line_of(op, a))
        if k in at and k != len(log):
            lines.append(winfb.line_of(winfb.DUMP << 4, [0] * 6))
    # winlink.py encode appends the final dump itself
    lines.append(winfb.line_of(winfb.END << 4, []))
    return '\n'.join(lines) + '\n'


def check_pins(out_hex, pins_path):
    import winfb
    import winlink
    recs = winlink.parse_up(winlink.read_hex(out_hex))
    data = [p for _s, t, p in recs if t == winlink.T_DATA]
    want = [ln.split() for ln in open(pins_path) if ln.strip()]
    if len(data) != 1280 * len(want):
        return '%d data records for %d pinned dumps' % (len(data), len(want))
    for k, (stage, sha) in enumerate(want):
        img = winfb.PBM_HEADER + bytes(b for p in data[1280 * k:1280 * (k + 1)] for b in p)
        got = hashlib.sha256(img).hexdigest()
        if got != sha:
            return 'dump %d (%s): sha256 %s, the pin %s' % (k, stage, got[:16], sha[:16])
    return ''


def main(argv):
    if len(argv) == 2 and argv[0] == 'streams':
        os.makedirs(argv[1], exist_ok=True)
        for case, (log, dumps) in kl0_logs().items():
            with open(os.path.join(argv[1], case + '.stream'), 'w') as f:
                f.write(stream_of(log, dumps))
            with open(os.path.join(argv[1], case + '.pins'), 'w') as f:
                for _n, s, p in dumps:
                    f.write('%s %s\n' % (s, p))
            print('win_kl0_link: %s: %d commands, dumps after %s' %
                  (case, len(log), ', '.join('%d (%s)' % (n, s) for n, s, _p in dumps)))
        return 0
    if len(argv) == 3 and argv[0] == 'pins':
        r = check_pins(argv[1], argv[2])
        if r:
            print('win_kl0_link pins: ' + r)
            return 1
        print('win_kl0_link pins: every dump read over the link = its test_espc.py pin')
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
