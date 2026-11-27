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
reads it and goes on into mendel_main's create/1: the mendel_title
process, its `Change phase ?` temporary_menu (stood in since 2026-11-27),
mendel_window's create_window/1 (font:kanji_16.font substituted, its
float sizes), and stops at `:create(#base, ...)`, MENDELS's class whose
natures are SIMPOS window mixins not held (labeled_sash, as_input,
as_superior, inferior_window, with_shared_window).  Re-recorded live
2026-11-27 from a copy of PROMPT.pkl: the exchanges and strings as
before, the stop and `where` new.

Injections, OBSERVED 2026-11-27 (24, each made in the working tree by a
scratch script, restored by copy, cmp and md5 clean; this whole file run
on each; the failed set as observed on the final file):

| injection | failed |
|---|---|
| espc split_repeat: the repeat dropped (the goals after it run once) | test_package, test_repeat |
| kl0 op_melt: the frozen term itself, no fresh variables | test_freeze_melt |
| kl0 op_freeze: the term itself, no copy | test_freeze_melt |
| espc classify: a component named by its bare name (no `Class$`) | test_component, test_replay, test_path_dialog |
| espc BUILTINS: object/3 dropped | test_package, test_replay, test_path_dialog |
| espc BUILTINS: atom/1, heap_vector/2 or not_equal_string/2 dropped (one at a time) | test_package |
| esp_reader: `::` not an operator | test_reader_package_colon, test_replay |
| read_one: no term without a `.` (end of text) | test_io_buffer_printed, test_reader_package_colon, test_replay, test_path_dialog |
| read_one: the layout after a `.` left unread | test_io_buffer_printed |
| putl/2: no newline after the string | test_io_buffer_printed, test_library_utility |
| putt/2: a compound written as {F,A,..} | test_io_buffer_printed |
| library_utility get_classes/4: every package's classes | test_library_utility |
| library_utility get_classes_with_wildcard/5: the pattern ignored | test_library_utility, test_replay, test_path_dialog |
| library_utility load/2 prints nothing | test_library_utility |
| symbolizer is_object/2 always true | test_io_window_title_and_object |
| process refute_in/5: the object and the arguments swapped | test_replay, test_path_dialog |
| as_event_handler get_instance/3 fails | test_replay, test_path_dialog |
| standard_io_window deactivate/1 a no-op | test_path_dialog |
| standard_io_window create/3: the title option ignored | test_io_window_title_and_object |
| standard_io_window name/2 succeeds with no name set | test_path_dialog |
| pmacs_window getl/2: the line from the point where getl began | test_getl |
| pathname check_pathname/3 fails | test_check_pathname, test_replay, test_path_dialog |

The temporary_menu step, OBSERVED 2026-11-27 (12 more, made and restored
the same way by a scratch script, cmp clean; this whole file run on each):

| injection | failed |
|---|---|
| read/2 answers the item_string, not the item_id | test_disc_loop, test_euod_pick |
| a no_select line can be chosen | test_disc_loop |
| the mouse leaving: the menu closed, no abort answered | test_disc_loop |
| label_flag(off) ignored (the title strip drawn) | test_disc_loop |
| the pop-up not at the mouse (at 0,0) | test_disc_loop, test_euod_pick, test_euod_shown |
| delete_item/2 deletes nothing | test_methods |
| add_item/3 appends (the position ignored) | test_methods |
| espc build: put_vector_n with n-1 | test_vector_puts |
| espc X/Y: the quotient over the second operand | test_floats |
| espc float constant: the cell holds the integer part | test_floats |
| kl0 floating_point_to_integer rounds up | test_floats |
| kl0 a float mixed with an integer: the integer taken as a float | test_floats |

Weak spots of this step: the replay catches none of the float or vector
injections (mendel_window's sizes are not drawn before the stop at
`#base`), and test_euod_leave none (an unanswered read leaves the same
calls and no pane): the unit tests and test_disc_loop carry them.

Weak spots: the replay does not reach repeat's retry, freeze/melt's
copies or putt's compound form (the run's terms are atoms and a list):
the unit tests carry them.  getl's line start is caught only by
test_getl (the run's old answers are empty); is_object/2 and the title
only by the direct test (the frames of the "WAIT !" window are not
pinned; the one frame pinned is the path dialog's).
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
STOP = ('simpos: send mendel##base:create/3 (not in the held classes; ancestors simpos##labeled_sash '
        'simpos##as_input simpos##as_superior simpos##inferior_window simpos##with_shared_window)')


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
        self.assertEqual(psi.where(7), ['mendel##mendel_window @2be', 'mendel##mendel_window @2c0',
                                        'mendel##mendel_window @29c', 'mendel##mendel_window @1d9',
                                        'mendel##mendel_window @19b', 'mendel##mendel_window @58',
                                        'mendel##mendel_main @c7'])

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
        # the archive's ESP half, its 108 .esp/.es files, as one package
        # (install.e Step 5-6): 18
        # items the parser drops (mdl_ckpred, mdl_cksyn, mdl_ckutil,
        # mendelmain :476 `****`, obj_editor, tsl_input), no class refused
        # whole, 402 predicates refused (1,122 before the built-ins,
        # repeat and components of 2026-11-27, 689 before vectors of up to
        # 255 elements and floats, the temporary_menu step)
        self.assertEqual(len(mendels.esp_sources()), 108)
        ts, rep = mendels.compile_package()
        self.assertEqual(len(rep['dropped']), 18)
        self.assertEqual(rep['failed'], {})
        self.assertEqual(len(rep['refused']), 402)
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
:after(C, X) :- freeze({f, A}, F), A = 1, melt(F, X);
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
        # the frozen copy keeps no link to the term frozen: binding A after
        # the freeze leaves the melted copy's variable unbound
        (r,) = K.call_class_method(m, 'user##fz', 'after', [K.Var()])
        self.assertIsInstance(K.deref(K.deref(r[0]).args[1]), K.Var)

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

    def test_vector_puts(self):
        # vectors of 1, 5, 6 and 8 elements built in a body: put_vector_1
        # .. put_vector_6 (b1-b6) and put_vector_n (b7 A 00 n), each row
        # KNOWN-PLAINTEXT (kl0_opcodes.tsv); MENDELS's items
        # {Label, common, Id, Doc, off} (lib_win.esp) are 5-vectors
        t = compile_one('''class vp has
:v(C, X, A, B, D, E) :- id({X}, A), id({X, common, X, _, off}, B), id({X, 2, 3, 4, 5, X}, D),
        id({X, 2, 3, 4, 5, 6, 7, X}, E);
local
id(V, V);
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##vp', 'v', [K.Atom('x')] + [K.Var() for _ in range(4)])
        got = [repr(K.resolve(a)) for a in r[1:]]
        self.assertEqual(got[0], '{x}')
        self.assertEqual(got[1].split(',')[:3], ['{x', 'common', 'x'])
        self.assertTrue(got[1].endswith(',off}'))
        self.assertEqual(got[2], '{x,2,3,4,5,x}')
        self.assertEqual(got[3], '{x,2,3,4,5,6,7,x}')
        text = espc.listing(t)
        for op in ('b1', 'b5', 'b6', 'b7'):
            self.assertRegex(text, r'\bpmi %s\b' % op, op)

    def test_floats(self):
        # floats (kl0.Flt; kl0_opcodes.tsv rows 6c, 6d, a8 with a float
        # cell): MENDELS's create_all_window/1 sizes (mendel_win.esp:
        # `Gh_f is BH_f * 0.8 - (Title_hf * 3.0)`) on the screen's 944
        # and a 21-dot title; X/Y on two registers (blt 43); the integer
        # back toward zero
        t = compile_one('''class fl has
:gh(C, BH, Title_h, Graph_h) :-
        integer_to_floating_point(BH, BH_f),
        integer_to_floating_point(Title_h, Title_hf),
        Gh_f is BH_f * 0.8 - (Title_hf * 3.0),
        floating_point_to_integer(Gh_f, Graph_h);
:quot(C, X, Y, Q) :- Q = X / Y;
:fq(C, X, Y, Q) :- integer_to_floating_point(X, F), integer_to_floating_point(Y, G),
        H = F / G + 0.5, floating_point_to_integer(H, Q);
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##fl', 'gh', [944, 21, K.Var()])
        # single precision: 944 * 0.8 = 755.2, - 63 = 692.2, toward zero
        self.assertEqual(K.resolve(r[2]), 692)
        (r,) = K.call_class_method(m, 'user##fl', 'quot', [17, 5, K.Var()])
        self.assertEqual(K.resolve(r[2]), 3)
        (r,) = K.call_class_method(m, 'user##fl', 'fq', [7, 2, K.Var()])
        self.assertEqual(K.resolve(r[2]), 4)        # 3.5 + 0.5
        text = espc.listing(t)
        self.assertRegex(text, r'\bblt 6c\b')
        self.assertRegex(text, r'\bblt 6d\b')
        self.assertRegex(text, r'\bblt 43\b')
        self.assertRegex(text, r'pmi a8 .*\n.*float 0\.8')
        # a float with an integer is refused when run (no witness of a
        # mixed operation)
        t2 = compile_one('''class fm has
:m(C, X, R) :- integer_to_floating_point(X, F), R = F * X;
end.''')
        m2 = K.Machine(espc.library([t2]))
        with self.assertRaises(K.Refusal):
            K.call_class_method(m2, 'user##fm', 'm', [3, K.Var()])


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

    def test_library_utility(self):
        # the loader's queries (loader.esp load_MENDEL/2) over kl0's library,
        # and load/2's `Loading <id>...` lines (ds_bep.esp:1992) to the
        # output set_output/2 gave
        m = self.m
        m.reset()
        (r,) = K.call_class_method(m, 'simpos##library_utility', 'create', [K.Var()])
        ut = K.deref(r[0])
        self.assertEqual(repr(K.resolve(self.send(ut, 'get_packages_with_wildcard',
                                                  self.string('mend*'), K.Var())[0][1])), '[mendel]')
        ((_, _, ids),) = self.send(ut, 'get_classes', self.string('mendel'), K.Atom('all'), K.Var())
        names = repr(ids)
        self.assertIn('mendel##mendel_main', names)
        self.assertNotIn('simpos##', names)
        ((_, _, _, ids),) = self.send(ut, 'get_classes_with_wildcard', self.string('mendel'),
                                      self.string('mendel_er*'), K.Atom('all'), K.Var())
        self.assertEqual(repr(ids), '[mendel##mendel_error]')
        # the output here a standard_io_buffer (its putl/2 a line)
        out = self.buffer()
        self.send(ut, 'set_output', out)
        self.assertEqual(len(self.send(ut, 'load', ids)), 1)
        self.assertEqual(K.deref(m.get_slot(out, 'text')).text, 'Loading mendel##mendel_error...\n')

    def test_io_window_title_and_object(self):
        # loader.esp:12-15: create/3's option title("WAIT !") is the
        # window's title; symbolizer is_object/2 on it and on the slot
        # value 0 the loader tests (load_MENDEL/2)
        m = self.m
        m.reset()
        opts = K.Cons(K.Vec([K.Atom('title'), self.string('WAIT !')]), K.NIL)
        (r,) = K.call_class_method(m, 'simpos##standard_io_window', 'create', [opts, K.Var()])
        w = K.deref(r[1])
        self.assertEqual(K.deref(m.get_slot(w, 'title')).text, 'WAIT !')
        sym = K.ClassRef('simpos##symbolizer')
        self.assertEqual(len(list(m.solve_send(sym, 'is_object', [w, sym]))), 1)
        self.assertEqual(list(m.solve_send(sym, 'is_object', [0, sym])), [])

    def test_models_labelled(self):
        # every kl0 model mendels_simpos installs has a label, and only those
        import mendels_simpos
        mine = {k for k, f in K.SIMPOS_MODELS.items() if getattr(f, '__module__', '') == 'mendels_simpos'}
        self.assertEqual(mine, set(mendels_simpos.LABELS))
        for k, v in mendels_simpos.LABELS.items():
            self.assertRegex(v, r'^(RECONSTRUCTED-FROM-MANUAL|INFERENCE|OURS)', k)

    def test_check_pathname(self):
        self.m.reset()
        p = self.string('>sys>user>MENDELuser')
        (r,) = K.call_class_method(self.m, 'simpos##pathname', 'check_pathname', [p, K.Var()])
        self.assertEqual(K.deref(r[1]).text, '>sys>user>MENDELuser')
        self.assertEqual(K.call_class_method(self.m, 'simpos##pathname', 'check_pathname',
                                             [self.string(''), K.Var()]), [])


class Menus(unittest.TestCase):
    """The temporary_menu stand-in (standin/temporary_menu.esp) through
    two other held users, run whole on the coordinator with the mouse:
    disc's system_data init/1 (the HELD files system_data.esp and
    util.esp, IFS natural-lang disc) and euod's syntax_print goal/1 (the
    HELD clause def.esp:821-835, verbatim, in an OURS harness class).
    Each program is started from the system menu after the login, as
    window M10's are (psi/test_espc.py pmacs_run), with the mouse at AT,
    so the menu's top-left is there."""
    AT = (300, 250)
    # OURS harness: disc's program calls :init(#system_data); the two
    # classes its select/2 sends to when `init` is chosen record the call
    DISC = """class tm_disc has
nature as_program;
attribute calls := [];
:note(Class, X) :- Class!calls := [X | Class!calls];
instance
:goal(P) :- :init(#system_data), :note(#tm_disc, done);
end.
class io_file has
:init(Class) :- :note(#tm_disc, init);
end.
class new_data_pool has
:create_chapter(Class);
end."""
    # OURS harness round the HELD goal/1 of euod's syntax_print: its
    # editor and theory database answer with atoms, print_file/2 and
    # print_buffer/3 (held ones print on a hardcopy window) record
    EUOD = """class tm_euod has
nature as_program;
attribute calls := [];
:note(Class, X) :- Class!calls := [X | Class!calls];
:create(Class, Obj) :- :new(Class, Obj), Obj!editor := Class, Obj!theory_db := Class;
:current_buffer(Class, buffer);
:get_font(Class, font);
:get_theory_name(Class, theory);
instance
attribute editor, theory_db;
%s
    :print_file(Obj,Theory_name):- :note(#tm_euod, {print_file, Theory_name});
    :print_buffer(Obj,Buffer,Font):- :note(#tm_euod, {print_buffer, Buffer, Font});
end.
class messenger has
:show(Class, S) :- :note(#tm_euod, shown);
end."""
    # frames: (sha256 of the PBM, set dots); the euod menu's committed as
    # docs/simpos/screens/temporary_menu.png
    SCREEN = os.path.join(HERE, '..', 'docs', 'simpos', 'screens', 'temporary_menu.png')

    @staticmethod
    def euod_goal():
        import held
        lines = held.member_text('euod_def').splitlines()
        g = lines[820:835]
        assert g[0].strip() == ':goal(Obj):-' and g[-1].strip().startswith(':show(#messenger,'), g
        return '\n'.join(g)

    def run_menu(self, prog, *batches):
        import fep_bridge as FB
        import held
        psi = FB.PsiSide()
        m = psi.m
        if prog == 'disc':
            srcs = [espc.esplex.decode(held.member_text(n).encode('latin-1'))[0]
                    for n in ('disc_system_data', 'disc_util')] + [self.DISC]
        else:
            srcs = [self.EUOD % self.euod_goal()]
        for src in srcs:
            ts, failed = espc.compile_text(src, 'simpos')
            self.assertEqual(failed, {})
            for t in ts:
                m.lib.add(t)
        psi.user = [FB.mouse('rr', *FB.MENU_AT), FB.mouse('l', *FB.LOGIN_ITEM_AT)]

        def start(mm):
            # disc's class slot opens font:kanji_16.font (system_data.esp:
            # 11-12): the substitute entry MENDELS's run has
            mendels.substitute_font(mm, 'kanji_16.font', 'test_11.font')
            C = K.ClassRef('simpos##coordinator')
            item = K.Vec([FB.jstr('TM'), K.Atom('tm_' + prog)])
            mm.set_slot(C, 'menu', K.Cons(K.Cons(item, K.NIL), mm.get_slot(C, 'menu')))
            return [self.move(*self.AT), K.Atom('invoke_system_menu'),
                    K.Vec([K.Atom('select'), FB.jstr('TM')])]
        rest = [start] + [list(b) for b in batches]

        def exchange(out):
            if rest and not psi.shell:
                b = rest.pop(0)
                psi.shell, psi.getl = list(b(m) if callable(b) else b), True
            return []
        stop = psi.run(exchange)
        self.assertEqual((rest, psi.shell), ([], []))
        self.assertEqual(stop.cause, 'would suspend')
        return m

    @staticmethod
    def move(x, y):
        return K.Vec([K.Atom('move'), x, y])

    @staticmethod
    def left(x, y):
        import fep_bridge as FB
        return FB.mouse('l', x, y)

    @staticmethod
    def calls(m, cls):
        out, t = [], K.deref(m.get_slot(K.ClassRef('simpos##' + cls), 'calls'))
        while isinstance(t, K.Cons):
            out.append(repr(K.resolve(t.args[0])))
            t = K.deref(t.args[1])
        return out

    def pane(self, m):
        C = K.ClassRef('simpos##coordinator')
        P = K.deref(m.get_slot(C, 'menu_pane'))
        if P == 0:
            return None
        return tuple(K.resolve(m.get_slot(P, k)) for k in ('x', 'y', 'w', 'h', 'items_top', 'label'))

    def test_euod_shown(self):
        # euod's `WHICH?` menu (create/3 with items_list of 5-field items
        # and title, then show/1, read/2): at the mouse, titled, two items
        # (the frame committed); nothing chosen yet
        import windev
        m = self.run_menu('euod')
        self.assertEqual(self.pane(m), (300, 250, 180, 55, 271, K.Atom('on')))
        fr = windev.device(m).frame
        self.assertEqual(windev.read_cells(fr, 302, 253, 16, 1), ['     WHICH?'])
        with open(self.SCREEN, 'rb') as f:
            self.assertEqual(windev.png_bytes(fr), f.read())
        self.assertEqual(self.calls(m, 'tm_euod'), [])

    def test_euod_pick(self):
        # a left click on the second item: read/2 gives its item_id
        # saved_syntax (TM-125 p18), the held goal takes that branch:
        # get_theory_name/2, print_file/2, the messenger; the menu is off
        # the screen (read/2 takes it down: euod hides nothing)
        m = self.run_menu('euod', [self.move(390, 295), self.left(390, 295)])
        self.assertEqual(self.calls(m, 'tm_euod'), ['shown', '{print_file,theory}'])
        self.assertIsNone(self.pane(m))

    def test_euod_leave(self):
        # the mouse leaves the menu: read/2 gives abort (TM-125 p18), which
        # neither branch of the held goal takes: nothing printed
        m = self.run_menu('euod', [self.move(390, 295), self.move(100, 100)])
        self.assertEqual(self.calls(m, 'tm_euod'), [])
        self.assertIsNone(self.pane(m))

    def test_disc_loop(self):
        # disc's initialisation menu (label_flag(off), label_font, set_font,
        # the show/read/hide loop of system_data init/1): no title strip;
        # a click on the no_select first line does nothing; `init` (the
        # third item) is answered and select/2 runs (:init(#io_file)),
        # fails as held (`!, fail`) and the menu is shown again; the mouse
        # leaving answers abort and init/1 returns
        import windev
        m = self.run_menu('disc')
        self.assertEqual(self.pane(m), (300, 250, 246, 84, 252, K.Atom('off')))
        self.assertEqual((windev.pbm_sha256(windev.device(m).frame), windev.device(m).frame.count()),
                         self.DISC_FRAME)
        m = self.run_menu('disc', [self.left(400, 260)])
        self.assertEqual(self.pane(m), (300, 250, 246, 84, 252, K.Atom('off')))
        self.assertEqual(self.calls(m, 'tm_disc'), [])
        m = self.run_menu('disc', [self.left(400, 260)], [self.left(400, 292)])
        self.assertEqual(self.calls(m, 'tm_disc'), ['init'])
        # shown again at the mouse, where the click was (TM-125 p7)
        self.assertEqual(self.pane(m), (400, 292, 246, 84, 294, K.Atom('off')))
        m = self.run_menu('disc', [self.left(400, 292)], [self.move(100, 100)])
        self.assertEqual(self.calls(m, 'tm_disc'), ['done', 'init'])
        self.assertIsNone(self.pane(m))

    DISC_FRAME = ('7dd50c95d2f7a0e8cea089df0aab41fcdbbc58d97a473462f7eae07b000d77ad', 103510)

    def test_methods(self):
        # the methods no run above reaches, on MENDELS's own `Change phase
        # ?` menu (mendelmain.esp:69-72): add_item/3 at a position and
        # add_items/3 (TM-125 p15), delete_item/2 by label, set_title/2,
        # set_item_status/3 kept, beep/1 counted, kill/1 (`alive` no, disc
        # util.esp:148), clear_items/1
        psi = mendels.PsiSide()
        m = psi.m
        m.reset()

        def s(text):
            x = K.Str('')
            x.text = text
            return x

        def item(label, value):
            return K.Vec([s(label), K.Atom('common'), K.Atom(value), K.Var()])

        def send(obj, name, *args):
            return [[K.resolve(a) for a in args] for _ in m.solve_send(obj, name, list(args) + [obj])]

        opts = K.Cons(K.Vec([K.Atom('title'), s('Change phase ?')]),
                      K.Cons(K.Vec([K.Atom('items_list'),
                                    K.Cons(item('    Yes    ', 'yes'), K.Cons(item('    No     ', 'no'), K.NIL))]),
                             K.NIL))
        (r,) = K.call_class_method(m, 'simpos##temporary_menu', 'create', [opts, K.Var()])
        M = K.deref(r[1])

        def labels():
            out, t = [], K.deref(m.get_slot(M, 'items'))
            while isinstance(t, K.Cons):
                out.append(K.deref(K.deref(t.args[0]).args[0]).text.strip())
                t = K.deref(t.args[1])
            return out
        self.assertEqual(labels(), ['Yes', 'No'])
        self.assertEqual(K.deref(m.get_slot(M, 'title')).text, 'Change phase ?')
        send(M, 'add_item', item('Maybe', 'maybe'), 1)
        self.assertEqual(labels(), ['Yes', 'Maybe', 'No'])
        send(M, 'add_items', K.Cons(item('A', 'a'), K.Cons(item('B', 'b'), K.NIL)), 3)
        self.assertEqual(labels(), ['Yes', 'Maybe', 'No', 'A', 'B'])
        send(M, 'delete_item', s('Maybe'))
        self.assertEqual(labels(), ['Yes', 'No', 'A', 'B'])
        send(M, 'set_title', s('T'))
        self.assertEqual(K.deref(m.get_slot(M, 'title')).text, 'T')
        send(M, 'set_item_status', K.Atom('yes'), K.Atom('on'))
        self.assertEqual(repr(K.resolve(m.get_slot(M, 'status'))), '[[yes,on]]')
        send(M, 'beep')
        self.assertEqual(K.resolve(m.get_slot(M, 'beeps')), 1)
        send(M, 'kill')
        self.assertEqual(K.resolve(m.get_slot(M, 'alive')), K.Atom('no'))
        send(M, 'clear_items')
        self.assertEqual(labels(), [])


def read(text):
    import mendels_simpos
    t, _rest = mendels_simpos.read_one(K, text)
    return t


if __name__ == '__main__':
    unittest.main()
