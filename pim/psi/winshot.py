#!/usr/bin/env python3
"""Write the live Login PIMOS screens as PNGs (window M5, OURS rendering of
the HELD test_11 font).

Each screen is a live kl0 run: boot, the system menu, Login PIMOS, the
held pimfep##pimos_login_requester and the keys of one stage of
test_espc.py Window.SCREENS (the same runs the test pins).  The PNG is the
whole device frame, 1,280 x 1,024 dots, one bit a dot (psi/windev.py
png_bytes, stdlib zlib only); the frame's PBM sha256 is printed beside it
and must equal the test's PINS.

Use:  python3 -I psi/winshot.py OUTDIR [STAGE ...]   (stages: name,
      password, login; all when none is given)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    import test_espc as T
    import windev
    out = argv[0]
    os.makedirs(out, exist_ok=True)
    T.Window.setUpClass()
    t = T.Window('test_win_m5_login_screen')
    stages = argv[1:] or list(T.Window.SCREENS)
    bad = 0
    for stage in stages:
        keys = T.Window.SCREENS[stage][0]
        _m, _p, _w, dev = t.screen(keys)
        path = os.path.join(out, 'login_pimos_%s.png' % stage)
        with open(path, 'wb') as f:
            f.write(windev.png_bytes(dev.frame))
        pin = (windev.pbm_sha256(dev.frame), dev.frame.count())
        ok = pin == T.Window.PINS[stage]
        bad += not ok
        print('%s  %s  %d dots  %s' % (path, pin[0], pin[1], 'pinned' if ok else 'DIFFERS FROM THE PIN'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
