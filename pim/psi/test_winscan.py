#!/usr/bin/env python3
"""Unit tests of the TMDS reference psi/wintmds.py and the scan-out model
psi/winscan.py (window_hardware_plan.md H2).  Each test pins a fact
written down by hand here or printed in a source, not computed by the
module:
  - the four control characters as DVI 1.0 Fig. 3-5 p29 prints them
    (q_out[0:9], bit 0 first) and as [9:0] values;
  - "one of 460 unique 10-bit characters during active data" (DVI 1.0
    §3.2.2 p28);
  - three characters of a run of 0x00 from cnt 0, worked by hand through
    Fig. 3-5 (0x100, 0x3ff, 0x100);
  - every byte decodes back from every reachable disparity (Fig. 3-6);
  - the mode table against the Linux drm_edid.c lines (sync start, sync
    end, total), and the frame rates of the plan's §2.2;
  - the 2:1 view's 2x2 OR, the pan, the border, and the cursor's modular
    position, on hand-made frames.

Run: python3 -I psi/test_winscan.py
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wintmds as T  # noqa: E402
import winscan as S  # noqa: E402
import winfb as F  # noqa: E402


class TestTmds(unittest.TestCase):
    def test_control_characters(self):
        # DVI 1.0 Fig. 3-5: 00: q_out[0:9] = 0010101011, etc.
        self.assertEqual(T.CTRL[0], 0b1101010100)
        self.assertEqual(T.CTRL[1], 0b0010101011)
        self.assertEqual(T.CTRL[2], 0b0101010100)
        self.assertEqual(T.CTRL[3], 0b1010101011)
        for c in range(4):
            self.assertEqual(T.encode(5, False, c, 0x37), (T.CTRL[c], 0))
            self.assertEqual(T.decode(T.CTRL[c], False), ('c', c))

    def test_460_data_characters(self):
        states, syms = T.reachable()
        self.assertEqual(len(syms), 460)
        self.assertEqual(sorted(states), list(range(-8, 9, 2)))
        self.assertFalse(syms & set(T.CTRL.values()))

    def test_zero_run_by_hand(self):
        # 0x00: N1 = 0, the XOR branch, q_m = 0, q_m[8] = 1.
        # cnt 0 -> q = {~1, 1, q_m} = 0x100, cnt = 0 + (0 - 8) = -8;
        # cnt -8 < 0 and N0 > N1 -> q = {1, 1, ~q_m} = 0x3ff, cnt = -8 + 2 + 8 = 2;
        # cnt 2: neither -> q = {0, 1, q_m} = 0x100, cnt = 2 - 0 + (0 - 8) = -6.
        q1, c = T.encode(0, True, 0, 0)
        q2, c = T.encode(c, True, 0, 0)
        q3, c = T.encode(c, True, 0, 0)
        self.assertEqual((q1, q2, q3, c), (0x100, 0x3ff, 0x100, -6))

    def test_round_trip_and_disparity(self):
        states, _ = T.reachable()
        for cnt in states:
            for d in range(256):
                q, c2 = T.encode(cnt, True, 0, d)
                self.assertEqual(T.decode(q, True), ('d', d))
                self.assertEqual(c2, cnt + T.disparity(q))

    def test_constant_runs_bounded(self):
        for d in (0x00, 0xff, 0x20, 0x80, 0x7f):
            cnt, run = 0, 0
            for _ in range(200):
                q, cnt = T.encode(cnt, True, 0, d)
                run += T.disparity(q)
                self.assertLessEqual(abs(run), 8)


class TestModes(unittest.TestCase):
    def test_drm_edid_lines(self):
        for n, (hss, hse, ht, vss, vse, vt) in S.DRM.items():
            m = S.MODES[n]
            self.assertEqual((m['ha'] + m['hf'], m['ha'] + m['hf'] + m['hs'],
                              S.totals(m)[0]), (hss, hse, ht), n)
            self.assertEqual((m['va'] + m['vf'], m['va'] + m['vf'] + m['vs'],
                              S.totals(m)[1]), (vss, vse, vt), n)
        self.assertEqual(S.totals(S.MODES[2]), (1440, 1054))     # the plan's

    def test_rates(self):
        def hz(n):
            ht, vt = S.totals(S.MODES[n])
            return S.MODES[n]['khz'] * 1000 / (ht * vt)
        self.assertAlmostEqual(hz(0), 30.0, places=3)
        self.assertAlmostEqual(hz(1), 60.02, places=2)
        self.assertAlmostEqual(hz(2), 49.41, places=2)   # the plan: 49.4
        self.assertAlmostEqual(hz(3), 59.94, places=2)

    def test_letterbox_centred(self):
        m = S.MODES[0]
        self.assertEqual((m['x0'], m['y0']), (320, 28))
        self.assertEqual(2 * m['x0'] + 1280, 1920)
        self.assertEqual(2 * m['y0'] + 1024, 1080)

    def test_line_ctrl(self):
        m = S.MODES[3]                       # -H -V
        de, c = S.line_ctrl(m, 0)
        self.assertEqual(sum(de), 640)
        hs = [k for k in range(800) if (c[k] & 1) == 0]
        self.assertEqual(hs, list(range(656, 752)))
        de, c = S.line_ctrl(m, 490)
        self.assertEqual(sum(de), 0)
        self.assertTrue(all((x >> 1) == 0 for x in c))   # vsync active, low
        de, c = S.line_ctrl(m, 492)
        self.assertTrue(all((x >> 1) == 1 for x in c))


class TestView(unittest.TestCase):
    def rows(self, mn):
        return S.frame_rows(F.run_stream(F.assemble(mn + '\nend\n')).dumps[-1])

    def test_half_or(self):
        m = S.MODES[3]
        rows = self.rows('fill 3 1 1 1 set\nfill 6 6 1 1 set')
        lev = S.line_levels(m, (0, 0), rows, (0, 0, 0, 0), None, 0)
        self.assertEqual(lev[:4], [S.WHITE, S.BLACK, S.WHITE, S.WHITE])
        lev = S.line_levels(m, (0, 0), rows, (0, 0, 0, 0), None, 3)
        self.assertEqual(lev[:4], [S.WHITE, S.WHITE, S.WHITE, S.BLACK])
        # pan 1 row: dot (3, 1) is in pair row 0 still; (6, 6) moves to row 2
        lev = S.line_levels(m, (0, 1), rows, (0, 0, 0, 0), None, 2)
        self.assertEqual(lev[3], S.BLACK)

    def test_border_and_window(self):
        m = S.MODES[0]
        rows = self.rows('fill 0 0 1 1 set')
        self.assertEqual(S.line_levels(m, (0, 0), rows, (0, 0, 0, 0), None, 27),
                         [S.BORDER] * 1920)
        lev = S.line_levels(m, (0, 0), rows, (0, 0, 0, 0), None, 28)
        self.assertEqual(lev[319:322], [S.BORDER, S.BLACK, S.WHITE])
        self.assertEqual(lev[1600], S.BORDER)
        self.assertEqual(S.line_levels(m, (0, 0), rows, (0, 0, 0, 0), None, 1080), [])

    def test_cursor_mask_and_wrap(self):
        m = S.MODES[2]
        rows = self.rows('fill 0 0 16 16 set')
        sh = [[(0x8001, 0x8000)] * 16] * 8         # mask: dots 0, 15; image: dot 0
        lev = S.line_levels(m, (0, 0), rows, (1, 4095, 0, 0), sh, 0)
        # x = 4095 is -1: shape dot 15 lands on u = 14 (white, mask 1, image 0)
        self.assertEqual(lev[13:16], [S.BLACK, S.WHITE, S.BLACK])
        lev = S.line_levels(m, (0, 0), rows, (1, 100, 0, 0), sh, 0)
        self.assertEqual(lev[100], S.BLACK)
        self.assertEqual(lev[101], S.WHITE)          # mask 0: the frame (white)
        self.assertEqual(lev[115], S.WHITE)          # mask 1, image 0

    def test_cases_config(self):
        for name in S.CASES:
            w = S.config_words(name)
            self.assertEqual(len(w), 160)
            self.assertTrue(all(0 <= v < 1 << 32 for v in w))
        self.assertEqual(S.config_words('mode0')[0], 0)
        self.assertEqual(S.config_words('rand1')[0], 15)
        self.assertEqual(S.config_words('mode0')[20], 2200 * 1125 + 2 * 2200)


if __name__ == '__main__':
    unittest.main()
