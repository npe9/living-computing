#!/usr/bin/env python3
"""MENDELS (IFS No.61) on PIMOS and SIMPOS together (psi/mendels.py),
and the pieces added for it (2026-11-27).

The run: the KL1 half on PIMOS, from the shell's prompt, installed as
readme.e/install.e say (the doc route), the ESP half compiled by espc.py
and run on kl0, linked by the FEP's string I/O.  Its tape,
psi/mendels_tapes/doc.json, was recorded by

    python3 -I psi/mendels.py live PROMPT.pkl --record psi/mendels_tapes/doc.json

(PROMPT.pkl: ref/pimm/ifs_sweep.py's header).  The live run is opt-in
(MENDELS_LIVE=PROMPT.pkl, about 80 s); the replay feeds the PSI side
PIMOS's packets from the tape and checks each packet the PSI sends.

Furthest point (OBSERVED, both runs): MENDELS's own ESP device starts,
asks the user's path in its pmacs_window dialog (init_path.esp; the keys
>sys>user>MENDELuser RETURN y RETURN), answers PIMOS load_library, PIMOS
loads mdllibrary.exe from >sys>user>MENDELuser>SYSTEM (the path typed)
and sends loaded_library(normal([mendel::example1, ...])); the ESP side
reads it and goes on into mendel_main's create/1, which stops at the
first SIMPOS class not stood in: temporary_menu:create/3.

Injections, OBSERVED 2026-11-27 (each in the working tree by a script,
restored by copy, cmp and md5 clean; this whole file run on it; the
failed set as observed):

| injection | failed |
|---|---|
| espc split_repeat: the repeat dropped (the goals after it kept, run once) | test_package, test_repeat |
| kl0 op_melt: the frozen term itself, no fresh variables | test_freeze_melt |
| espc classify: a component named by its bare name (no `Class$`) | test_component, test_replay, test_path_dialog |
| mendels_simpos read_one: no term without a `.` (end of text) | test_io_buffer_printed, test_reader_package_colon, test_replay, test_path_dialog |
| mendels_simpos putt/2: a compound written as {F,A,..} | test_io_buffer_printed |
| esp_reader: `::` not an operator | test_reader_package_colon, test_replay |
| pmacs_window getl/2: the line from the point where getl began | test_getl |
| pathname check_pathname/3 fails | test_check_pathname, test_replay, test_path_dialog |
| standard_io_window name/2 succeeds with no name set | test_path_dialog |

Weak spots: the replay does not reach repeat's retry, melt's fresh
variables or putt's compound form (the run's terms are atoms and a
list); getl's line start is caught only by test_getl, since the run's old
answers are empty; the loader's name/2 test only through the screen.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import espc  # noqa: E402
import kl0 as K  # noqa: E402
import mendels  # noqa: E402

TAPE = os.path.join(HERE, 'mendels_tapes', 'doc.json')
SCREEN = os.path.join(HERE, '..', 'docs', 'simpos', 'screens', 'mendels_path.png')

# the string-I/O messages of the run (mendels.strings_io), OBSERVED live
# 2026-11-27: the devices PIMOS makes by 601, its io (620) and the PSI's
# answers.  The answer to 56's io(0, "system") is the user path typed in
# the dialog, with >SYSTEM> (esp_util.esp)
STRINGS_IO = [
    ('create', 38, 'mendel##mendel_esp_device'), ('close', 38),
    ('create', 39, 'mendel##esp_utility'), ('>', 39, 2, '>sys>user>MENDEL>KL1>'), ('close', 39),
    ('create', 41, 'mendel##mendel_esp_device'), ('<', 39, 1, 'end'), ('close', 41),
    ('create', 42, 'mendel##mendel_loader'), ('create', 44, 'mendel##mendel_esp_device'),
    ('>', 42, 0, 'mendel'), ('close', 44),
    ('create', 46, 'mendel##mendel_esp_device'), ('<', 42, 1, 'end'), ('close', 46),
    ('create', 47, 'mendel##esp_utility'), ('>', 47, 2, '>sys>user>MENDEL>KL1>'), ('close', 47),
    ('create', 49, 'mendel##mendel_esp_device'), ('<', 47, 1, 'end'), ('close', 49),
    ('create', 50, 'mendel##mendel_esp_device'), ('>', 50, 0, 'start'),
    ('create', 52, 'mendel##mendel_esp_device'), ('<', 50, 1, 'load_library'), ('close', 52),
    ('create', 53, 'mendel##esp_utility'), ('>', 53, 2, '>sys>user>MENDEL>KL1>'), ('close', 53),
    ('create', 55, 'mendel##mendel_esp_device'), ('<', 53, 1, 'end'), ('close', 55),
    ('create', 56, 'mendel##esp_utility'), ('>', 56, 0, 'system'), ('close', 56),
    ('create', 62, 'mendel##mendel_esp_device'),
    ('>', 50, 0, 'loaded_library(normal([mendel:: example1,mendel:: example2,mendel:: example3]))'),
    ('<', 56, 1, '>sys>user>MENDELuser>SYSTEM>'),
]
STOP = 'simpos: send simpos##temporary_menu:create/3 (class class not loaded)'


def load_tape():
    with open(TAPE) as f:
        return json.load(f)


class Run(unittest.TestCase):
    def test_tape(self):
        # the tape's own record: the live run's string I/O and its stop
        tape = load_tape()
        self.assertEqual(mendels.strings_io(tape), STRINGS_IO)
        self.assertEqual(tape['result']['stop'], STOP)
        self.assertEqual(len(tape['exchanges']), 21)

    def test_replay(self):
        # the PSI side, fed the tape: every packet it sends is the live
        # run's, it uses up the tape, and it stops where the live run did
        stop, psi, left = mendels.replay(TAPE)
        self.assertEqual('%s: %s' % (stop.cause, stop.detail), STOP)
        self.assertEqual(left, [])
        self.assertEqual(psi.where(2), ['mendel##mendel_main @b4', 'mendel##mendel_main @b6'])

    def test_path_dialog(self):
        # init_path.esp's dialog after the path is typed, before y: the
        # frame committed as docs/simpos/screens/mendels_path.png
        import windev
        stop, psi, left = mendels.replay(TAPE, keys=['>sys>user>MENDELuser'], lenient=True)
        self.assertEqual(stop.cause, 'would suspend')
        self.assertIn('mendel##mendel_path', ' '.join(psi.where(12)))
        with open(SCREEN, 'rb') as f:
            self.assertEqual(windev.png_bytes(windev.device(psi.m).frame), f.read())

    @unittest.skipUnless(os.environ.get('MENDELS_LIVE'), 'MENDELS_LIVE=PROMPT.pkl runs PIMOS (~80 s)')
    def test_live(self):
        result, _psi, _pim = mendels.live(os.environ['MENDELS_LIVE'], record=None)
        self.assertEqual(result['stop'], STOP)
        self.assertEqual(result['exchanges'], 21)


class Compile(unittest.TestCase):
    def test_package(self):
        # the archive's ESP half as one package (install.e Step 5-6): 18
        # items the parser drops (mdl_ckpred, mdl_cksyn, mdl_ckutil,
        # mendelmain :476 `****`, obj_editor, tsl_input), no class refused
        # whole, 689 predicates refused (1,122 before the built-ins,
        # repeat and components of 2026-11-27)
        ts, rep = mendels.compile_package()
        self.assertEqual(len(rep['dropped']), 18)
        self.assertEqual(rep['failed'], {})
        self.assertEqual(len(rep['refused']), 689)
        ids = {t.id for t in ts}
        for c in ('mendel##mendel_esp_device', 'mendel##mendel_loader', 'mendel##esp_utility',
                  'mendel##mendel_path', 'mendel##mendel_main'):
            self.assertIn(c, ids)

    def test_repeat(self):
        # `repeat` (espc split_repeat): the goals after it are retried
        # until they succeed; a slot is not undone on backtracking
        t = compile_one('''class rp has
attribute n := 0;
:loop(C, K, N) :- C!n := 0, repeat, C!n := C!n + 1, C!n >= K, !, N = C!n;
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##rp', 'loop', [3, K.Var()])
        self.assertEqual(K.resolve(r[1]), 3)

    def test_freeze_melt(self):
        # freeze/2 and melt/2 (blt 3e, 3f; ESP manual program-e.tex
        # 1895-1939): each melt gives fresh variables, shared as in the
        # term frozen
        t = compile_one('''class fz has
:t(C, X, Y) :- freeze({f, A, A, B}, F), melt(F, X), melt(F, Y);
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##fz', 't', [K.Var(), K.Var()])
        x, y = [K.deref(a) for a in r]
        xe = [K.deref(e) for e in x.args]
        ye = [K.deref(e) for e in y.args]
        self.assertIs(xe[1], xe[2])
        self.assertIsNot(xe[1], xe[3])
        self.assertIsNot(xe[1], ye[1])
        self.assertIsInstance(xe[1], K.Var)

    def test_component(self):
        # a component's slot is pkg##class$name (KNOWN-PLAINTEXT
        # qxt##name_table new_expr/2 @4e), read and set by that name
        t = compile_one('''class cm has
component buf := 0;
:put(C, X) :- C!buf := X;
:get(C, X) :- X = C!buf;
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        self.assertEqual(len(K.call_class_method(m, 'user##cm', 'put', [7])), 1)
        (r,) = K.call_class_method(m, 'user##cm', 'get', [K.Var()])
        self.assertEqual(K.resolve(r[0]), 7)
        self.assertIn('user##cm$buf', t.symbols)


def compile_one(text):
    ts, failed = espc.compile_text(text, 'user')
    assert not failed, failed
    (t,) = ts
    return t


class Simpos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.psi = mendels.PsiSide()
        cls.m = cls.psi.m

    def send(self, obj, name, *args):
        m = self.m
        regs = list(args) + [obj]
        return [[K.resolve(a) for a in args] for _ in m.solve_send(obj, name, regs)]

    def string(self, text):
        s = K.Str('')
        s.text = text
        return s

    def buffer(self):
        (r,) = K.call_class_method(self.m, 'simpos##standard_io_buffer', 'create', [K.Var()])
        return K.deref(r[0])

    def test_io_buffer_printed(self):
        # the ESP manual's Example 3 (program-e.tex 6733-6745), PRINTED
        self.m.reset()
        b = self.buffer()
        self.send(b, 'putl', self.string('p(1,2).'))
        self.send(b, 'putl', self.string('[1,2].'))
        (cp,) = self.send(b, 'gett', K.Var())
        self.assertEqual(repr(cp[0]), repr(K.resolve(read('p(1,2)'))))
        (ls,) = self.send(b, 'gett', K.Var())
        self.assertEqual(repr(ls[0]), repr(K.resolve(read('[1,2]'))))
        self.send(b, 'putt', read('[1,2]'))
        self.send(b, 'putt', read('p(1,2)'))
        (s,) = self.send(b, 'getl', K.Var())
        self.assertEqual(K.deref(s[0]).text, '[1,2]p(1,2)')
        with self.subTest('end-of-text term (INFERENCE, MENDELS main.kl1 call_loop/3)'):
            self.send(b, 'reset')
            self.send(b, 'putl', self.string('load_library'))
            self.send(b, 'reread')
            (a,) = self.send(b, 'gett', K.Var())
            self.assertEqual(repr(a[0]), repr(K.Atom('load_library')))

    def test_reader_package_colon(self):
        # `Package::Module`, as PIMOS writes the loaded modules
        t = read('normal([mendel::example1])')
        self.assertEqual(repr(K.resolve(t)), '{normal,[{::,mendel,example1}]}')

    def test_getl(self):
        # pmacs_window getl/2 (init_path.esp read_string/3: the old answer
        # put at the point, then getl): after a prompt putl/2 wrote, `abc`
        # in the buffer and the keys d e BS f RETURN, the line is abcdf
        m = self.m
        m.reset()
        (r,) = K.call_class_method(m, 'simpos##pmacs_window', 'create', [K.NIL, K.Var()])
        w = K.deref(r[1])
        self.send(w, 'activate')
        ((b,),) = self.send(w, 'current_buffer', K.Var())
        self.send(w, 'putl', self.string('prompt'))
        self.send(b, 'insert_string', self.string('abc'))
        i = m.get_slot(w, 'interpreter')
        d, e, f = K.Str('def').codes()       # the codes the keys give (fep_bridge.key_script)
        for x in (d, e, 8, f, 13):
            self.send(i, 'input', x)
        ((line,),) = self.send(w, 'getl', K.Var())
        self.assertEqual(K.deref(line).text, 'abcdf')

    def test_check_pathname(self):
        self.m.reset()
        p = self.string('>sys>user>MENDELuser')
        (r,) = K.call_class_method(self.m, 'simpos##pathname', 'check_pathname', [p, K.Var()])
        self.assertEqual(K.deref(r[1]).text, '>sys>user>MENDELuser')
        self.assertEqual(K.call_class_method(self.m, 'simpos##pathname', 'check_pathname',
                                             [self.string(''), K.Var()]), [])


def read(text):
    import mendels_simpos
    t, _rest = mendels_simpos.read_one(K, text)
    return t


if __name__ == '__main__':
    unittest.main()
