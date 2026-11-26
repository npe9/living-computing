#!/usr/bin/env python3
"""Write the live window screens as PNGs (windows M4-M10, OURS rendering of
the HELD test_11 font).

Each screen is a live kl0 run, the same run test_espc.py Window pins:
  - name, password, login: boot, the system menu, Login PIMOS, the held
    pimfep##pimos_login_requester and the keys of one stage of
    Window.SCREENS, with the 3m probe for PIMOS;
  - bridged: step 3n's run, the held requester logged into real PIMOS,
    PIMOS replayed from the committed tape
    psi/fep_bridge_tapes/login_pwd.json, so its replies are login.kl1's;
  - console (window M4): PIMOS's console window bridged to the PSI,
    replayed from psi/fep_bridge_tapes/console_pwd.json: `Shell>> `,
    the typed `pwd`, PIMOS's answer, beside the Login PIMOS window;
  - menu (window M6): the boot screen with the system menu opened by the
    right button and its "Login PIMOS" item boxed;
  - over (window M7): the system menu opened over the Login PIMOS window,
    whose dots its save area keeps (test_win_m7_save_areas);
  - popup, sweep (window M6): with Login PIMOS shown, its item chosen
    again: the `create`/`kill` pop-up; then `create`, a corner, a move:
    the rubber-band outline (test_win_m6_create_kill);
  - manip, hidden, reshaped (window M7): with a second requester's window
    over the Login PIMOS window, the window manipulator opened on it by
    the middle button; that window hidden under the other by HIDE; it
    reshaped by RESHAPE (test_win_m7_manip);
  - expand, windows, notify (window M7's other items and permissions):
    window 2, moved clear of window 1, grown by EXPAND; the
    manipulator's MENU submenu listing the windows (test_win_m7_items);
    the notify window of window 2, covered by window 1 as it echoes
    (test_win_m7_permissions);
  - graphics (window M8): a window of 40 x 20 cells with a filled block,
    the HELD paragraph icon box drawn by execute_graphics_command/2, a
    slanted line, a string, a clipped fill and a transfer
    (test_win_m8_graphics);
  - graphics_rest (window M8's rest): the HELD g_window bar views with
    their held pattern strings, the HELD type_switch_icon draw/6 (its
    image through restore_image/6), and the shapes (test_win_m8_rest_screen);
  - choice (window M9): the HELD pimfep superviser's error mode menu, a
    standard_choice_window (test_win_m9_choice);
  - attribute (window M9): the manipulator's ATTRIBUTE sheet on window 2
    (test_win_m9_attribute);
  - pmacs (window M10): the HELD disc/exshow.esp's Pmacs window on
    me:boot.init after `Hi`, C-n, `x`, C-x C-s: the edited text, the
    reversed mode line, the echo line `Written! ...` (test_win_m10_exshow);
  - editor_menu (window M10): the EDITOR MENU opened on that window by the
    right button (test_win_m10_menu).
The PNG is the whole device frame, 1,280 x 1,024 dots, one bit a dot
(psi/windev.py png_bytes, stdlib zlib only); the frame's PBM sha256 is
printed beside it and must equal the test's pin.

Use:  python3 -I psi/winshot.py OUTDIR [STAGE ...]   (stages: name,
      password, login, bridged, console, menu, over, popup, sweep, manip,
      hidden, reshaped, expand, windows, notify, graphics, graphics_rest,
      choice, attribute, pmacs, editor_menu; all when none
      is given)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

NAMES = {'console': 'pimos_console', 'menu': 'system_menu', 'over': 'menu_over_window',
         'popup': 'create_kill_popup', 'sweep': 'rubber_band', 'manip': 'window_manipulator',
         'hidden': 'manipulator_hide', 'reshaped': 'manipulator_reshape',
         'expand': 'manipulator_expand', 'windows': 'manipulator_menu', 'notify': 'notify_window',
         'graphics': 'window_graphics', 'graphics_rest': 'window_graphics_rest',
         'choice': 'choice_window', 'attribute': 'manipulator_attribute',
         'pmacs': 'pmacs_editor', 'editor_menu': 'editor_menu'}


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    import test_espc as T
    import windev
    import fep_bridge as FB
    K = T.K
    out = argv[0]
    os.makedirs(out, exist_ok=True)
    T.Window.setUpClass()
    t = T.Window('test_win_m5_login_screen')
    stages = argv[1:] or list(T.Window.SCREENS) + ['bridged', 'console', 'menu', 'over', 'popup', 'sweep',
                                                   'manip', 'hidden', 'reshaped', 'expand', 'windows',
                                                   'notify', 'graphics', 'graphics_rest', 'choice',
                                                   'attribute', 'pmacs', 'editor_menu']
    bad = 0
    for stage in stages:
        if stage == 'bridged':
            frame = windev.device(t.bridged()).frame
            want = T.Window.BRIDGED_PIN
        elif stage == 'console':
            psi, _t = t.console()
            frame = windev.device(psi.m).frame
            want = T.Window.CONSOLE_PIN
        elif stage == 'menu':
            _m, frame = t.menu_run(FB.mouse('rr', *FB.MENU_AT),
                                   K.Vec([K.Atom('move')] + list(FB.LOGIN_ITEM_AT)))
            want = T.Window.MENU_PINS['boxed']
        elif stage == 'graphics':
            _m, frame = t.graphics_run()
            want = T.Window.GRAPHICS_PIN
        elif stage == 'graphics_rest':
            _m, frame = t.graphics_rest_run()
            want = T.Window.GRAPHICS_REST_PIN
        elif stage == 'choice':
            _m, frame, _menu = t.choice_run()
            want = T.Window.CHOICE_PIN
        elif stage in T.Window.M10_PINS:
            _m, frame, _stop = t.pmacs_run('exshow', *T.Window.m10_shots()[stage])
            want = T.Window.M10_PINS[stage]
        elif stage in T.Window.SHOT_PINS:
            _m, frame, _stop = t.later_run(*T.Window.shot_events()[stage]())
            want = T.Window.SHOT_PINS[stage]
        else:
            _m, _p, _w, dev = t.screen(T.Window.SCREENS[stage][0])
            frame = dev.frame
            want = T.Window.PINS[stage]
        path = os.path.join(out, '%s.png' % NAMES.get(stage, 'login_pimos_' + stage))
        with open(path, 'wb') as f:
            f.write(windev.png_bytes(frame))
        pin = (windev.pbm_sha256(frame), frame.count())
        ok = pin == want
        bad += not ok
        print('%s  %s  %d dots  %s' % (path, pin[0], pin[1], 'pinned' if ok else 'DIFFERS FROM THE PIN'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
