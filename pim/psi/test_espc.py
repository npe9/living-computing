#!/usr/bin/env python3
"""Tests of the ESP compiler (psi/espc.py).  OURS.

    python3 -I psi/test_espc.py        (about 25 seconds; reads the held
                                        source and .ptf files in memory,
                                        extracts nothing)

1. Emission: every cell the compiler produces for paragraph's held source
   has a row in psi/kl0_opcodes.tsv, and nothing is refused as an
   internal error.
2. The language questions the compiler settled: `X =< Y` is blt 67 with
   the operands swapped (`>=` not); `X+Y` on two registers, `=\\=` and an
   unknown built-in refuse, naming the construct.
3. Structure against paragraph.ptf (`espc.py check paragraph`): class
   aspects, the predicate counts and named exact matches pinned; no two
   predicates under one comparison key; every paired `$or$` has the
   held arity.
4. Behaviour: the compiled paragraph classes ALONE in a library (so every
   class a call reaches is compiled here) give test_kl0.py's answers;
   paragraph_version gives the held source's "3200" where paragraph.ptf
   gives "3500" (the known build skew).  On kl0's census of
   paragraph.ptf no method runs to a different outcome.
5. Macro banks (`with_macro`, TM-388 §3.7.3): expansion on a compiled
   example (own rules before the natures', a `:-` rule refusing its
   predicate), and kappa2's structure against kappa.ptf pinned (all 739
   classes compile; 1,361 predicates cell for cell, 1,323 before the
   string built-ins).
6. Slot initialisation in kl0's new/2 on compiled classes (TM-388 §3.5
   pp.48-50): instance and class slots, a failing initialiser fails new,
   an unbound value refuses, an after-demon of new sees the slots.
7. Stand-ins (psi/standin/): every method carries a PRINTED or
   INTERPOLATED label (the owner's rule, 2026-11-24); `:self(#process,P)`
   gives one process instance, made by :new, which runs the printed
   slot initialisers of TM-100 Fig. 3.1 (four lists and a clock);
   pimfep##pimos_timer on_after/4, which refused at
   simpos##process:self/2, gets through the interpolated tag_catch/9
   (:refute, TM-388 p.46) and refuses at process:allow_forced_event/1;
   the interpolated string append/3 and copy/3, and the partial
   symbolizer's string_to_list/3 and list_to_string/3, run on the four
   string built-ins; tag_catch/5 sends put/2 to a stream through :refute;
   pimos_timer's class stream/2, which stopped at kl0's new/2 (the
   printed stream's slots are initialised by code), succeeds, and the
   printed put/2 and get/2 run first in, first out; kl0's census of
   pimfep and pimscsi is pinned.

Discriminating (2026-11-24; each bug injected into espc.py from a backup
copy in the session scratchpad, the observed failures recorded, the file
restored with cp and checked with cmp):
  - parser: a disjunction keeps only its first alternative: test_counts
    and test_compiled_answers fail;
  - register allocation: the lowest free register starts at A1: the
    compiler raises (not a refusal) on paragraph, so every test that
    compiles it errors: setUpClass of Behaviour, test_counts,
    test_named_exact, test_aspect_differences and both Emission tests;
  - cut operand: d4 n = envsize instead of 8 + envsize: only test_counts
    fails (kl0 does not read d4's n, so behaviour is unchanged);
  - slot flag: the attribute flag 0x10 dropped: test_counts and
    test_aspect_differences fail;
  - demon kind: instance before and after swapped: test_counts and
    test_aspect_differences fail;
  - language: `=<` compiled without the operand swap: test_compare and
    test_compiled_answers fail (get_code's `Y =< Icon!height/2`).
  - macro bank: a bank's natures not inherited: test_expansion and
    test_kappa2 fail;
  - macro bank: an expansion not expanded again: test_expansion and
    test_kappa2 fail;
  - macro bank: the natures' rules tried before the bank's own: only
    test_expansion fails;
  - macro bank: rules with a `:-` tail applied as plain rules: only
    test_expansion fails;
  - stand-in label (injected into standin/stream.esp): get/2's PRINTED
    label reworded: only test_methods_labelled fails.
  The injections into kl0.py's slot initialisation, the string
  built-ins and :refute, and espc's head-save fix, and what they fail
  here, are recorded in test_kl0.py's header.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import espc  # noqa: E402
import kl0 as K  # noqa: E402

_CHECK = None
_LIB_SIX = None


def check():
    global _CHECK
    if _CHECK is None:
        _CHECK = espc.check('paragraph')
    return _CHECK


def compile_one(text):
    ts, failed = espc.compile_text(text, 'user')
    assert not failed, failed
    (t,) = ts
    return t


def code(t, name):
    (p,) = [p for p in t.preds() if p is not None and p.name == name]
    return [(c[1], c[3] >> 24, (c[3] >> 16) & 255, (c[3] >> 8) & 255) for c in p.cells
            if c[1] in (0x20, 0x21)]


class Emission(unittest.TestCase):
    def test_only_witnessed_opcodes(self):
        rows = {(r['class'], r['opcode']) for r in K.load_table()}
        ts, _failed = espc.compiled_program('paragraph')
        seen = set()
        for t in ts:
            for p in t.preds():
                if p is None:
                    continue
                for c in p.cells:
                    if c[1] in (0x20, 0x21):
                        seen.add(('pmi' if c[1] == 0x20 else 'blt', '%02x' % (c[3] >> 24)))
        self.assertEqual(seen - rows, set())
        self.assertGreater(len(seen), 40)

    def test_no_internal_refusal(self):
        for p in ('paragraph', 'utter'):
            r = espc.check(p) if p != 'paragraph' else check()
            self.assertNotIn('internal', r['refusals'], p)


class Language(unittest.TestCase):
    T = '''class t has
:le(C,X,Y) :- X =< Y;
:ge(C,X,Y) :- X >= Y;
:add(C,X,Y,Z) :- Z = X+Y;
:ne(C,X,Y) :- X =\\= Y;
:inc(C,X,Z) :- Z = X+1;
instance
:foo(O) :- frob(O);
end.'''

    def test_compare(self):
        t = compile_one(self.T)
        # receiver last: X in A0, Y in A1.  X =< Y is `67 Y X`
        self.assertEqual(code(t, 'le'), [(0x21, 0x67, 1, 0), (0x20, 0xf0, 0, 0)])
        self.assertEqual(code(t, 'ge'), [(0x21, 0x67, 0, 1), (0x20, 0xf0, 0, 0)])
        self.assertEqual(code(t, 'inc')[0], (0x21, 0x45, 0, 1))

    def test_refusals_name_the_construct(self):
        t = compile_one(self.T)
        got = {r[0][0]: r[1] for r in t.refusals}
        self.assertEqual(got, {'add': 'arithmetic X+Y', 'ne': 'comparison =\\=',
                               'foo': 'built-in frob/1'})


class Structure(unittest.TestCase):
    def test_counts(self):
        c = check()['counts']
        self.assertEqual((c['templates'], c['with source'], c['classes compiled']), (121, 109, 109))
        self.assertEqual([c['%s agree' % a] for a in ('natures', 'slots', 'methods', 'locals')],
                         [109, 108, 108, 109])
        self.assertEqual(c['demon sets agree'], 109)
        # 991 compared, 243 exact before the string built-ins (string/3,
        # new_string/3, string_element/3, set_string_element/3) and the
        # head-save fix (a permanent head variable after a structured
        # argument: 246 -> 247), 2026-11-24
        self.assertEqual((c['pred compared'], c['pred exact']), (1051, 247))
        self.assertEqual(c['key collisions'], 0)
        self.assertEqual(c['$or$ paired with another arity'], 0)
        self.assertEqual(c['pred compiled only'], 0)

    def test_aspect_differences(self):
        # paragraph_version: the version slot, "3200" in the source and
        # "3500" in the .ptf; h_grade: two of its items do not parse
        rows = [(r[0], r[1]) for r in check()['rows'] if r[2] == 'aspect differs']
        self.assertEqual(rows, [('paragraph##paragraph_version', 'slots'),
                                ('paragraph##h_grade', 'methods')])

    def test_named_exact(self):
        got = {(r[0], r[1]): r[2] for r in check()['rows']}
        for cid, preds in (
                ('paragraph##icon_button', ['create/2 25', 'create/4 25', 'create/6 25',
                                            'set_position/3 35', 'set_size/3 35']),
                ('paragraph##list_index_buffer', ['add_first/3 35', 'add_last/3 35', 'count/2 35',
                                                  'create/2 25', 'get_contents/2 35',
                                                  'get_partial_contents/4 35', 'search/2 35',
                                                  'search_num/4 35'])):
            for p in preds:
                self.assertEqual(got[(cid, p)], 'exact', (cid, p))


class Behaviour(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = espc.behave()

    def test_compiled_answers(self):
        c, h = self.r['calls']
        for k in c:
            self.assertNotIn('REFUSED', c[k], k)
            self.assertNotIn('STEP', c[k], k)
        A = 'inc_predicate_num', 'dec_predicate_num'
        sw = c['predicate_num_switch_icon create/3 + get_code/4']
        for y0, want in ((210, A[0]), (228, A[0]), (229, A[1]), (240, A[1])):
            self.assertIn('%d: [[105, %d, %s]]' % (y0, y0, want), sw)
        self.assertEqual(c['list_index_buffer battery'],
                         "[1, [[3]], [[[c,a,b]]], [[[{c,kc},{a,ka},{b,kb}]]], [[kb, b]], "
                         "[[kb, b, 3]], [[kc]], 1, [], [[2]], [[[c,b]]], [[1, 5, [{b,kb}]]], "
                         "[[5, 5, []]], [[kb, 2]]]")
        self.assertEqual(c['scroll_bottom_icon code/4'],
                         '[[[0, 0, scroll_bottom], [0, 0, bottom_predicate]], '
                         '[[0, 0, bottom_predicate]], [[0, 0, scroll_bottom]], []]')
        for k in c:
            if k != 'paragraph_version get_version/1':
                self.assertEqual(c[k], h[k], k)

    def test_version_skew(self):
        c, h = self.r['calls']
        self.assertEqual(c['paragraph_version get_version/1'], "[[string#'3200']]")
        self.assertEqual(h['paragraph_version get_version/1'], "[[string#'3500']]")

    def test_census(self):
        self.assertEqual(dict(self.r['census']), {'same outcome': 88, 'both refused': 87,
                                                  'refused compiled only': 46,
                                                  'refused held only': 6})


class MacroBank(unittest.TestCase):
    """`with_macro` (TM-388 §3.7.3 pp.72-75): a bank's plain clause-level
    rules expand head arguments and body terms top-down; a bank inherits
    its natures' rules, its own first; an unmodelled rule form refuses
    the predicate that meets it."""
    T = '''add_operator(@,fx,100).
macro_bank mb0 has
@k0 => 7;
@k1 => 8;
end.
macro_bank mb has
nature mb0;
@k => 5;
@k0 => 99;
pair(X) => {X, @k};
cond(X) => X :- true;
end.
class t with_macro mb has
:a(C, X) :- X = @k;
:b(C, Y) :- Y = pair(2);
:c(C, Z) :- Z = @k0;
:d(C, Z) :- Z = cond(1);
:e(C, @k1);
end.'''

    def test_expansion(self):
        ts, failed = espc.compile_text(self.T, 'user')
        self.assertEqual(failed, {})
        (t,) = ts
        self.assertEqual([(r[0][0], r[1]) for r in t.refusals], [('d', 'macro rule')])
        m = K.Machine(espc.library(ts))
        got = {sel: K.call_class_method(m, 'user##t', sel, [K.Var()])
               for sel in ('a', 'b', 'c', 'e')}
        self.assertEqual(repr(got), "{'a': [[5]], 'b': [[{2,5}]], 'c': [[99]], 'e': [[8]]}")

    def test_kappa2(self):
        # espc.py check kappa2, 2026-11-24.  Before with_macro: 335 of 739
        # classes compiled (404 refused whole), 3,387 predicates compared,
        # 501 exact.  After: all 739 compile; 9,971 compared, 1,323 exact.
        # Of the exact ones, 822 are in the 406 classes with a bank, and
        # 109 of those have source clauses that a bank rule changed: the
        # expansion meets the held cells (structural witness).
        r = espc.check('kappa2')
        c = r['counts']
        self.assertEqual((c['classes compiled'], c['class refused']), (739, 0))
        # with the string built-ins (step 3b): 10,641 compared, 1,361 exact
        self.assertEqual((c['pred compared'], c['pred exact']), (10641, 1361))
        self.assertEqual([c['%s agree' % a] for a in ('natures', 'slots', 'methods', 'locals')],
                         [738, 738, 736, 736])
        self.assertEqual((r['refusals']['macro rule'], r['refusals']['internal']), (40, 2))
        self.assertNotIn('with_macro', r['refusals'])


class SlotInit(unittest.TestCase):
    """kl0's new/2 runs compiled slot-initialisation predicates (TM-388
    §3.5 pp.49-50): instance slots at new, class slots when the class is
    generated (first class-slot access, OURS); a failing predicate makes
    new fail (and the class not generated); an unbound value refuses
    (TM-388 p.48: a slot cannot hold an unbound variable); an after-demon
    of new sees the initialised instance (TM-388 p.50)."""
    T = '''class t has
attribute (cs := V :- V = 5);
:get_cs(C, X) :- X = C!cs;
instance
attribute a := 1, (b := Y :- Y = 2), (c := Z :- Z = {Y, 3});
end.
class t2 has
after :new(C, O) :- O!a := 10;
instance
attribute a := 1, (b := Y :- Y = 2), (c := Z :- Z = {2, 3});
:get(O, A, B, C) :- A = O!a, B = O!b, C = O!c;
end.
class u has
instance
attribute (b := Y :- fail);
end.
class v has
attribute (cs := V :- fail);
:get_cs(C, X) :- X = C!cs;
end.'''

    @classmethod
    def setUpClass(cls):
        ts, failed = espc.compile_text(cls.T, 'user')
        assert not failed and not any(t.refusals for t in ts)
        cls.m = K.Machine(espc.library(ts))

    def new(self, cid):
        m = self.m
        return [K.resolve(m.x[0]) for _ in m.solve_send(K.ClassRef(cid), 'new',
                                                       [K.Var(), K.ClassRef(cid)])]

    def test_instance_slots_and_after_demon(self):
        (o,) = self.new('user##t2')
        regs = [K.Var(), K.Var(), K.Var(), o]
        got = [[K.resolve(r) for r in regs[:3]] for _ in self.m.solve_send(o, 'get', regs)]
        self.assertEqual(repr(got), '[[10, 2, {2,3}]]')

    def test_failure_fails_new(self):
        self.assertEqual(self.new('user##u'), [])

    def test_unbound_refuses(self):
        with self.assertRaises(K.Refusal) as e:
            self.new('user##t')
        self.assertEqual(e.exception.cause, 'slot init unbound')

    def test_class_slot(self):
        (s,) = K.call_class_method(self.m, 'user##t', 'get_cs', [K.Var()])
        self.assertEqual(s, [5])
        with self.assertRaises(K.Refusal) as e:
            K.call_class_method(self.m, 'user##v', 'get_cs', [K.Var()])
        self.assertEqual(e.exception.cause, 'class not generated')


class Standins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ts = espc.standins()
        cls.plain = K.Machine(K.load_six())
        lib = K.load_six()
        for t in cls.ts:
            lib.add(t)
        cls.m = K.Machine(lib)

    def refusal(self, m, cid, section, sel):
        name, n = sel.rsplit('/', 1)
        n = int(n)
        m.reset()
        recv = K.ClassRef(cid) if section == 'class' else K.make_instance(m, cid)
        regs = [K.Var() for _ in range(n - 1)] + [recv]
        with self.assertRaises(K.Refusal) as e:
            any(True for _ in m.solve_send(recv, name, regs))
        return e.exception.cause, e.exception.detail

    def test_compiled_whole(self):
        self.assertEqual(sorted(t.id for t in self.ts), [
            'simpos##list', 'simpos##post_queue', 'simpos##process', 'simpos##process_clock',
            'simpos##stream', 'simpos##string', 'simpos##symbolizer',
            'simpos##waiting_frame', 'simpos##waiting_queue', 'simpos##with_link'])
        for t in self.ts:
            self.assertEqual(t.refusals, [], t.id)

    def test_methods_labelled(self):
        # owner's rule (2026-11-24): each stand-in method is labelled
        # PRINTED or INTERPOLATED in the comment block just above it (its
        # first clause: a head indented at most 4, as the files are laid out;
        # a body goal is indented further).  Locals are not methods.
        for t in self.ts:
            with open(os.path.join(espc.STANDIN, t.name + '.esp')) as f:
                lines = f.read().splitlines()
            for p in t.preds():
                if p is None or p.kind in (0x11, 0x12, 0x22, 0x32):
                    continue
                (i,) = [k for k, x in enumerate(lines) if x.strip().startswith(':%s(' % p.name)
                        and len(x) - len(x.lstrip()) <= 4][:1]
                j = i - 1
                block = []
                while j >= 0 and lines[j].strip().startswith('%'):
                    block.append(lines[j])
                    j -= 1
                self.assertTrue(any('PRINTED:' in x or 'INTERPOLATED' in x for x in block),
                                (t.id, p.name))

    def test_self(self):
        (a,) = K.call_class_method(self.m, 'simpos##process', 'self', [K.Var()])
        (b,) = K.call_class_method(self.m, 'simpos##process', 'self', [K.Var()])
        self.assertIsInstance(a[0], K.Instance)
        self.assertIs(a[0], b[0])

    def test_on_after_gets_further(self):
        cid, sel = 'pimfep##pimos_timer', 'on_after/4'
        cause, detail = self.refusal(self.plain, cid, 'instance', sel)
        self.assertEqual(cause, 'simpos')
        self.assertIn('simpos##process:self/2', detail)
        cause, detail = self.refusal(self.m, cid, 'instance', sel)
        self.assertEqual(cause, 'simpos')
        # tag_catch/9 (interpolated, :refute) now runs the timer's
        # do_on_after/3, which stops at the next lost method
        self.assertIn('simpos##process:allow_forced_event/1 (not in the stand-in)', detail)

    def strs(self, *xs):
        t = K.NIL
        for x in reversed(xs):
            t = K.Cons(K.Str(x), t)
        return t

    def test_string(self):
        # the interpolated string stand-in on the four witnessed string
        # built-ins (blt 0b, 1c, 23, 2b)
        m = self.m
        (r,) = K.call_class_method(m, 'simpos##string', 'append',
                                   [self.strs('ab', '::', 'c d'), K.Var()])
        s = r[1]
        self.assertEqual((repr(s), s.type, len(s.codes())), ("string#'ab::c d'", 16, 7))
        (r,) = K.call_class_method(m, 'simpos##string', 'append', [self.strs(), K.Var()])
        self.assertEqual(repr(r[1]), "string#''")
        (c,) = K.call_class_method(m, 'simpos##string', 'copy', [s, K.Var()])
        self.assertEqual(repr(c[1]), "string#'ab::c d'")
        self.assertIsNot(c[1], s)
        # the partial symbolizer: string_to_list/3 and list_to_string/3
        # (kap_serv.esp's space_delete/2 deletes 8481, the JIS space, from
        # the list between the two)
        (r,) = K.call_class_method(m, 'simpos##symbolizer', 'string_to_list', [K.Var(), s])
        codes = [K.resolve(x) for x in s.codes()]
        self.assertEqual(repr(r[0]), repr(codes).replace(' ', ''))
        lst = K.NIL
        for x in reversed([x for x in codes if x != 8481]):
            lst = K.Cons(x, lst)
        (r,) = K.call_class_method(m, 'simpos##symbolizer', 'list_to_string', [lst, K.Var()])
        self.assertEqual((repr(r[1]), r[1].type), ("string#'ab::cd'", 16))
        (r,) = K.call_class_method(m, 'simpos##symbolizer', 'list_to_string', [K.NIL, K.Var()])
        self.assertEqual(repr(r[1]), "string#''")

    def test_refute(self):
        # tag_catch/5 (interpolated) calls :refute(Object, Method, Args)
        # (TM-388 p.46): a put/2 sent to a stream through it
        m = self.m
        (p,) = K.call_class_method(m, 'simpos##process', 'self', [K.Var()])
        (st,) = K.call_class_method(m, 'simpos##stream', 'create', [K.Var()])
        proc, st = p[0], st[0]
        m.reset()
        args = [st, K.Atom('put'), K.Vec([K.Atom('hello'), ]), K.Atom('abort'), proc]
        self.assertEqual(sum(1 for _ in m.solve_send(proc, 'tag_catch', args)), 1)
        regs = [K.Var(), st]
        self.assertEqual([repr(K.resolve(regs[0])) for _ in m.solve_send(st, 'get', regs)], ['hello'])

    def test_stream_runs(self):
        # pimos_timer's class stream/2 used to stop at kl0's new/2 (the
        # printed stream's slots are initialised by code); with new/2
        # running them and the post_queue / waiting_queue stand-ins it
        # succeeds
        cid, sel = 'pimfep##pimos_timer', 'stream/2'
        cause, detail = self.refusal(self.plain, cid, 'class', sel)
        self.assertIn('simpos##stream:create/2', detail)
        m = self.m
        m.reset()
        regs = [K.Var(), K.ClassRef(cid)]
        self.assertTrue(any(True for _ in m.solve_send(K.ClassRef(cid), 'stream', regs)))
        # the printed put/2 and get/2: first in, first out; get on an empty
        # stream fails (the printed suspend/2 fails for a process whose
        # status is nil: the stand-in's one process is never activated)
        (s,) = K.call_class_method(m, 'simpos##stream', 'create', [K.Var()])
        st = s[0]
        self.assertEqual([x.cid for x in st.slots], ['simpos##post_queue', 'simpos##waiting_queue'])

        def send(name, *args):
            regs = list(args) + [st]
            return [[K.resolve(a) for a in args] for _ in m.solve_send(st, name, regs)]
        self.assertEqual(len(send('put', K.Atom('a'))), 1)
        self.assertEqual(len(send('put', 7)), 1)
        self.assertEqual(repr(send('get', K.Var())), '[[a]]')
        self.assertEqual(repr(send('get', K.Var())), '[[7]]')
        self.assertEqual(send('get', K.Var()), [])

    def test_printed_process_slots(self):
        # :self(#process,P) makes the process with :new, which runs the
        # printed slot initialisers (TM-100 Fig. 3.1): four lists and a clock
        (a,) = K.call_class_method(self.m, 'simpos##process', 'self', [K.Var()])
        co = self.m.lib.build('simpos##process')
        got = {e.name: v for e, v in zip(co.instance_slots, a[0].slots)}
        for n in ('suspend_reasons', 'children_processes', 'invocation_stack', 'resources'):
            self.assertEqual(got[n].cid, 'simpos##list', n)
        self.assertEqual(got['clock'].cid, 'simpos##process_clock')
        self.assertEqual((got['mask_count'], repr(got['status'])), (0, 'nil'))
        self.assertTrue(co.complete)

    def test_fep_census(self):
        # kl0's census of pimfep and pimscsi (stand-ins loaded), 2026-11-24.
        # Before slot initialisation by code ran: 1,215 methods, 486
        # success, 50 failure, 679 refused (195 'slot init by code').
        # After it: 1,228, 501, 50, 677.  After the string built-ins
        # (blt 0b, 1c, 23, 2b), :refute and tag_catch: 515 success (14
        # methods that stopped at new_string/3), 51 failure (packet32
        # is_used/1, no longer refused), 662 refused.
        rows = K.census_fep(K.fep_machine())
        out = {}
        for r in rows:
            out[r[3]] = out.get(r[3], 0) + 1
        self.assertEqual((len(rows), out), (1228, {'success': 515, 'failure': 51, 'refused': 662}))
        self.assertNotIn('slot init by code', {r[4] for r in rows})


if __name__ == '__main__':
    unittest.main()
