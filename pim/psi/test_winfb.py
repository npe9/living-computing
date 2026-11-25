#!/usr/bin/env python3
"""Unit tests of the window device layer psi/winfb.py (OURS scaffolding;
window_hardware_plan.md H0/H1).  Each test pins a fact written down by
hand here, not computed by the module: exact bytes of an unaligned fill
(which a flipped bit order or a short edge mask changes), the PBM size,
XOR twice erasing, save/draw-over/restore being exact, overlapping copies
against a hand-shifted pattern, the 48 dots of test_11's 'A' at 16#2341
(window_environment_plan.md §1.4, MEASURED there with its recipe), and
the stream format round trip.

Run: python3 -I psi/test_winfb.py
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import winfb as F  # noqa: E402


def run(mn):
    return F.run_stream(F.assemble(mn + '\nend\n'))


def row_bytes(fr, y, n):
    return fr.pbm()[len(F.PBM_HEADER) + y * 160:][:n]


class TestFormat(unittest.TestCase):
    def test_record_layout(self):
        t = F.assemble('copy 1 2 3 4 5 65535 xor')
        self.assertEqual(t.split()[0], '42_0001_0002_0003_0004_0005_ffff')
        self.assertIn('// copy 1 2 3 4 5 65535 xor', t)
        self.assertEqual(F.parse_stream(t), [(0x42, [1, 2, 3, 4, 5, 65535])])

    def test_save_writes_copy_op(self):
        self.assertTrue(F.assemble('save 1 2 3 4 5 6').startswith('53_'))

    def test_no_end_is_an_error(self):
        with self.assertRaises(ValueError):
            F.run_stream(F.assemble('fill 1 1 1 1 set'))

    def test_bad_line(self):
        with self.assertRaises(ValueError):
            F.parse_stream('12_0000_0000\n')

    def test_every_stream_assembles_and_ends(self):
        for name in F.STREAMS:
            recs = F.parse_stream(F.gen(name))
            self.assertEqual(recs[-1][0], 0, name)


class TestFill(unittest.TestCase):
    def test_pbm_size(self):
        fr = run('')
        self.assertEqual(len(fr.dumps), 1)
        self.assertEqual(len(fr.dumps[0]), len(b'P4\n1280 1024\n') + 160 * 1024)
        self.assertEqual(fr.dumps[0][:13], b'P4\n1280 1024\n')

    def test_unaligned_fill_bytes(self):
        # dots 3..12 of row 1: 0001 1111  1111 1000
        fr = run('fill 3 1 10 2 set')
        self.assertEqual(row_bytes(fr, 0, 3), b'\x00\x00\x00')
        self.assertEqual(row_bytes(fr, 1, 3), b'\x1f\xf8\x00')
        self.assertEqual(row_bytes(fr, 2, 3), b'\x1f\xf8\x00')
        self.assertEqual(row_bytes(fr, 3, 3), b'\x00\x00\x00')
        self.assertEqual(fr.count(), 20)

    def test_word_crossing_fill(self):
        # dots 14..17: the last two of word 0 and the first two of word 1
        fr = run('fill 14 0 4 1 set')
        self.assertEqual(row_bytes(fr, 0, 4), b'\x00\x03\xc0\x00')

    def test_ops(self):
        fr = run('fill 0 0 8 1 set\nfill 2 0 4 1 reset')
        self.assertEqual(row_bytes(fr, 0, 1), b'\xc3')
        fr = run('fill 0 0 8 1 set\nfill 2 0 4 1 xor\nfill 7 0 2 1 xor')
        self.assertEqual(row_bytes(fr, 0, 2), b'\xc2\x80')
        fr = run('fill 0 0 4 1 copy\nfill 2 0 4 1 reverse')
        self.assertEqual(row_bytes(fr, 0, 1), b'\xc0')

    def test_xor_twice_erases(self):
        fr = run('fill 10 10 30 20 set\nfill 17 13 50 9 xor\n'
                 'fill 17 13 50 9 xor')
        self.assertEqual(fr.count(), 600)

    def test_clip(self):
        self.assertEqual(run('fill 1275 0 10 1 set').count(), 5)
        self.assertEqual(run('fill 0 1020 1 10 set').count(), 4)
        self.assertEqual(run('fill 1280 0 10 10 set').count(), 0)
        self.assertEqual(run('fill 0 0 0 10 set').count(), 0)
        self.assertEqual(run('fill 1279 1023 9 9 set').dot(1279, 1023), 1)

    def test_bad_op_draws_nothing(self):
        fr = F.Frame()
        fr.run([(0x17, [0, 0, 9, 9, 0, 0]), (0x90, [0] * 6), (0, [0] * 6)])
        self.assertEqual(fr.status, [F.BADOP, F.BADOP])
        self.assertEqual(fr.count(), 0)


class TestCopy(unittest.TestCase):
    def test_overlap_right_and_left(self):
        # row pattern 1100 1010 at dots 0..7, copied onto itself
        base = 'fill 0 0 2 1 set\nfill 4 0 1 1 set\nfill 6 0 1 1 set\n'
        fr = run(base + 'copy 0 0 8 1 3 0 copy')
        self.assertEqual(row_bytes(fr, 0, 2), b'\xd9\x40')   # 110 11001 010
        fr = run(base + 'copy 1 0 7 1 0 0 copy')
        self.assertEqual(row_bytes(fr, 0, 1), b'\x94')       # 1001010 0
        self.assertEqual(run(base + 'copy 0 0 8 1 3 0 copy').count(),
                         6)

    def test_overlap_down_and_up(self):
        base = 'fill 5 0 1 1 set\nfill 5 2 1 1 set\n'
        fr = run(base + 'copy 0 0 8 4 0 1 copy')
        self.assertEqual([fr.dot(5, y) for y in range(5)], [1, 1, 0, 1, 0])
        fr = run(base + 'copy 0 1 8 4 0 0 copy')
        self.assertEqual([fr.dot(5, y) for y in range(5)], [0, 1, 0, 0, 0])

    def test_copy_clip(self):
        fr = run('fill 0 0 20 20 set\ncopy 0 0 20 20 1270 1018 copy')
        self.assertEqual(fr.count(), 400 + 10 * 6)

    def test_reverse(self):
        fr = run('fill 0 0 3 1 set\ncopy 0 0 8 1 0 1 reverse')
        self.assertEqual(row_bytes(fr, 1, 1), b'\x1f')


class TestSave(unittest.TestCase):
    def test_hide_show_exact(self):
        draw = ('fill 100 100 77 33 set\nfill 103 104 13 5 xor\n'
                'fill 150 120 2 2 reset\n')
        want = run(draw).pbm()
        fr = run(draw + 'save 3 95 97 90 40 123\nfill 96 98 80 30 xor\n'
                 'restore 3 copy')
        self.assertEqual(fr.pbm(), want)
        self.assertEqual(fr.status, [0, 0, 0, 0, 0, 0])

    def test_errors(self):
        fr = run('restore 2 copy\nsave 16 0 0 1 1 0\n'
                 'save 0 0 0 1280 1024 0\nsave 0 0 0 16 2 65534\n'
                 'save 0 0 0 17 2 65534')
        self.assertEqual(fr.status, [F.NOSAVE, F.BADSAVE, F.BADSAVE,
                                     F.OK, F.BADSAVE])


class TestLine(unittest.TestCase):
    def test_horizontal_and_diagonal(self):
        self.assertEqual(run('line 0 0 9 0 1 65535 set').count(), 10)
        fr = run('line 3 3 0 0 1 65535 set')
        self.assertEqual([fr.dot(i, i) for i in range(4)], [1] * 4)
        self.assertEqual(fr.count(), 4)

    def test_style_and_width(self):
        fr = run('line 0 0 15 0 1 43690 set')    # 0xaaaa
        self.assertEqual(row_bytes(fr, 0, 2), b'\xaa\xaa')
        fr = run('line 0 0 0 9 3 65535 set')     # y-major: pen across x
        self.assertEqual(fr.count(), 30)
        self.assertEqual(run('line 0 0 9 0 0 65535 set').count(), 0)


class TestGlyph(unittest.TestCase):
    A = ['....###....', '...##.##...', '..##...##..', '..##...##..',
         '.##.....##.', '.##.....##.', '.##.....##.', '.#########.',
         '.##.....##.', '.##.....##.', '.##.....##.', '...........',
         '...........', '...........']

    def test_font_header(self):
        f = F.test_11()
        self.assertEqual((f.n, f.strip_bits, f.height, len(f.words)),
                         (128, 1408, 14, 2277))
        self.assertEqual(f.records[0x2341], (825, 0, 11, 14, 3))

    def test_A(self):
        fr = run('glyph 0 0x2341 5 7 set')
        self.assertEqual(fr.count(), 48)
        got = [''.join('#' if fr.dot(5 + i, 7 + j) else '.'
                       for i in range(11)) for j in range(14)]
        self.assertEqual(got, self.A)

    def test_missing_glyph_is_visible(self):
        # test_11's 0xffff record, drawn for a code the font lacks: a
        # boxed '?' of 50 dots (read 2026-11-25), so a gap is never blank
        fr = run('glyph 0 0x2122 0 0 set')
        self.assertEqual(fr.status, [F.MISSING])
        self.assertEqual(fr.count(), 50)
        self.assertEqual([fr.dot(x, 0) for x in range(11)], [1] * 11)
        self.assertEqual([fr.dot(0, y) for y in range(11)], [1] * 11)

    def test_login_prompt_all_held(self):
        codes = F.jis_text(F.LOGIN_PROMPT)
        self.assertEqual(len(codes), 29)
        fr = run('\n'.join('glyph 0 %d %d 0 set' % (c, 11 * i)
                           for i, c in enumerate(codes)))
        self.assertEqual(fr.status, [F.OK] * 29)
        self.assertGreater(fr.count(), 29 * 10)

    def test_opaque_and_missing(self):
        fr = run('fill 0 0 11 14 set\nglyph 0 0x2341 0 0 copy')
        self.assertEqual(fr.count(), 48)
        fr = run('fill 0 0 11 14 set\nglyph 0 0x2341 0 0 reverse')
        self.assertEqual(fr.count(), 154 - 48)
        fr = run('glyph 0 0x2122 0 0 set\nglyph 0 0xffff 20 0 set\n'
                 'glyph 2 0x2341 0 0 set')
        self.assertEqual(fr.status, [F.MISSING, F.OK, F.BADFONT])
        a = [fr.dot(i, j) for j in range(14) for i in range(11)]
        b = [fr.dot(20 + i, j) for j in range(14) for i in range(11)]
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
