#!/usr/bin/env python3
"""Tests of the ESP compiler (psi/espc.py).  OURS.

    python3 -I psi/test_espc.py        (about 17 s of CPU; reads the held
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
   classes compile; 1,485 predicates cell for cell, 1,361 before step
   3c's rows, 1,323 before the string built-ins).
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
8. Step 3c's stand-ins (2026-11-24): the printed channel's code-
   initialised post_queue slot overrides stream's, and the printed
   bounded_channel's plain slot overrides channel's, its printed
   bounded_post_queue's before- and after-demons taking and giving back
   the interpolated semaphore's tokens (a third put on a channel bounded
   at 2 fails until a get); list_index and hash_index on the entry
   layout kappa2's KPPOOL.ESP and SVHSH_IDX.ESP read; process create/3
   makes a dormant child of the calling process, and pimfep's own
   process/4 runs; the minimal standard_editor's get_window/2.
9. Step 3c's rows and HELD-SOURCE classes (2026-11-24): X+Y compiles
   (blt 40) and `(X+1)-X` reads X twice; the symbolizer's interpolated
   get_number/3 and get_number_string/3 on integers (a `.` refuses);
   morphana's _simpos/ name, e_string and pathname (ICOT Free Software,
   labelled HELD-SOURCE) run on substring/4, search_character/5 and
   string_tail/3, their remaining refusals pinned; pathname get_last/4's
   backward search refuses; on_after/4 now fails at integer/1 on an
   unbound argument and, given an integer, reaches alarm_watch (step
   3d: past it, to set_string_element on an unbound argument).
10. Step 3d's rows (2026-11-24): `{}` compiles to pmi b0, a four-element
   vector to pmi b4, and vector_to_list/3 and set_subvector/4 run.
   Step 3d's ten INTERPOLATED stand-ins: a class lock is undone on
   backtracking and nests; fep_device_table add_at/5 runs between
   :lock and :unlock; pimscsi cmt keeps a sender and a body;
   pmacs_window and its standard_editor point at each other; the FEP
   census is 1,265 methods, 665 success.
11. Step 3e (2026-11-24): the PRINTED as_program (TM-100 Fig. 3.3) with
   process's interpolated program stack (assign/resign_core/invoke), and
   kl0's rule that a missing primary under a stand-in ancestor stays
   SIMPOS; the FEP census pinned (1,403 methods, 782 success).

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
  - argument placement (step 3c, 2026-11-24): espc's clear_way fix
    reverted (an argument placed in a register that a later argument's
    move clears is read from the old register): only test_hash_index
    errors (its fill/3 loop stops after one bucket); `espc.py check` of
    paragraph, kappa2 and utter is unchanged with or without the fix;
  - list_index (injected into standin/list_index.esp): add_at/3 prepends
    instead of appending: test_list_index and test_hash_index fail;
  - semaphore (injected into standin/semaphore.esp): p_operation/1 takes
    a token without checking that one is left: only test_channel fails.
  - built-in inputs (step 3c): builtin() marks a variable's register as
    a value while later inputs are put, so `substring(S,H,T-H,P)` loses
    H: reverted, espc raises KeyError compiling e_string and paragraph:
    setUpClass of Behaviour and of Standins, test_counts,
    test_named_exact, test_aspect_differences, test_kappa2 and both
    Emission tests error;
  - arithmetic (step 3c): arith() does the same to Y in X-Y: reverted,
    the setUpClass of Behaviour, test_counts, test_named_exact,
    test_aspect_differences and both Emission tests error (KeyError) and,
    with `(X+1)-X` in Language's class, every Language test errors;
  - search_character (injected into kl0.py): the search starts one past
    B: only test_held_source fails (split of `ab>>c` and `>a`);
  - integer/1 (kl0.py): refuses an unbound argument instead of failing:
    test_on_after_gets_further errors and test_fep_census fails (here),
    test_step3c_cells errors (test_kl0.py);
  - stand-in label (standin/name.esp): ident/3's HELD-SOURCE label
    reworded: only test_methods_labelled fails.
  - `{}` (step 3d): espc's pmi b0 branch disabled, so `{}` is put as a
    pool constant: only test_step3d_vectors fails.  `espc.py check` does
    not see it (no predicate whose only difference is a `{}` is exact
    either way).
  - step 3d's stand-ins (each injected into standin/, restored by cp
    from a backup and cmp-checked): as_class_with_lock's :lock without
    its :unlock alternative: only test_step3d_lock fails; as_message
    get_sender/2 reading the receiver slot: only test_step3d_message
    fails; pmacs_window create/3 not setting the editor's window: only
    test_step3d_window_and_timer fails; common_network is_installed/1
    failing: only test_fep_census fails; with_lock's instance :lock
    without its :unlock alternative: only test_step3d_lock fails;
    message get_content/2 reading the sender slot: only
    test_step3d_message fails; alarm_watch wait/1 failing, and time
    set_count/2 failing: each only test_on_after_gets_further fails;
    network_listener_buffer create/4 failing, and trace trace/1
    failing: each test_step3d_window_and_timer and test_fep_census
    fail.
  - step 3e (same method, the session's inject.py; observed): kl0's
    stand-in-ancestor rule disabled: test_step3e_as_program and
    test_fep_census fail; process die/1 doing nothing, and no_program/1
    always failing: each only test_step3e_as_program fails.
  The injections into kl0.py's slot initialisation, the string
  built-ins and :refute, and espc's head-save fix, and what they fail
  here, are recorded in test_kl0.py's header.
"""
import os
import re
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
:mul(C,X,Y,Z) :- Z = X*Y;
:sub(C,X,Z) :- Z = (X+1)-X;
instance
:foo(O) :- frob(O);
end.'''

    def test_step3d_vectors(self):
        # step 3d (2026-11-24): `{}` is pmi b0 (typewin.esp:259
        # `:refute(PBEDIT,Item,{})` gives `b0 01`), not a pool constant; a
        # four-element vector is pmi b4 and four unify instructions
        # (p_tgraph.esp:299); vector_to_list/3 and set_subvector/4 run
        t = compile_one('''class v has
:r(C,P,I) :- :refute(P,I,{});
:four(C,A,B,D,E,L) :- vector_to_list({A,B,D,E},[],L);
:put(C,H) :- new_heap_vector(H,4), set_subvector(H,0,4,{1,2,3,4});
end.''')
        self.assertIn((0x20, 0xb0, 1, 0), code(t, 'r'))
        self.assertIn(0xb4, [c[1] for c in code(t, 'four') if c[0] == 0x20])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##v', 'four', [1, 2, 3, 4, K.Var()])
        self.assertEqual(repr(r[4]), '[1,2,3,4]')
        (r,) = K.call_class_method(m, 'user##v', 'put', [K.Var()])
        self.assertEqual([K.deref(e) for e in r[0].args], [1, 2, 3, 4])

    def test_compare(self):
        t = compile_one(self.T)
        # receiver last: X in A0, Y in A1.  X =< Y is `67 Y X`
        self.assertEqual(code(t, 'le'), [(0x21, 0x67, 1, 0), (0x20, 0xf0, 0, 0)])
        self.assertEqual(code(t, 'ge'), [(0x21, 0x67, 0, 1), (0x20, 0xf0, 0, 0)])
        self.assertEqual(code(t, 'inc')[0], (0x21, 0x45, 0, 1))

    def test_refusals_name_the_construct(self):
        t = compile_one(self.T)
        got = {r[0][0]: r[1] for r in t.refusals}
        # X+Y compiles since step 3c (blt 40, 2026-11-24); X*Y is still
        # refused
        self.assertEqual(got, {'mul': 'arithmetic X*Y', 'ne': 'comparison =\\=',
                               'foo': 'built-in frob/1'})

    def test_add_and_shared_operand(self):
        t = compile_one(self.T)
        # Z = X+Y: X (A0) copied to a free register, `40 r Y r`, the
        # result over the first operand as in h.esp:186 `40 01 00 01`
        self.assertIn(0x40, [c[1] for c in code(t, 'add') if c[0] == 0x21])
        # (X+1) - X: the right operand X stays X's register while the
        # left one reads it too (espc's arith(), step 3c; before the fix
        # it raised KeyError, so compiling T fails and with it every
        # Language test: injection, observed 2026-11-24)
        ops = [c[1] for c in code(t, 'sub') if c[0] == 0x21]
        self.assertEqual(ops[:2], [0x45, 0x41])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##t', 'add', [3, 4, K.Var()])
        self.assertEqual(K.resolve(r[2]), 7)
        (r,) = K.call_class_method(m, 'user##t', 'sub', [5, K.Var()])
        self.assertEqual(K.resolve(r[1]), 1)


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
        # argument: 246 -> 247), 2026-11-24.  1051 / 247 before the step 3c
        # rows (add, type tests, string_tail, equal_string, substring,
        # search_character, stack_vector): no exact predicate lost.
        # 1234 / 256 before step 3d's rows (vector_to_list, set_subvector,
        # `{}` and four-element vectors): none lost
        self.assertEqual((c['pred compared'], c['pred exact']), (1241, 258))
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
        # step 3c (X+Y compiled): 88 / 87 / 46 / 6 before.  The new
        # `refused held only` is graph_status_element set/2: the held
        # code stops at pmi 36 (a 6-element vector, no row), the compiled
        # code succeeds.  Step 3d (`{}`, four-element vectors,
        # set_subvector): 92 / 86 / 42 / 7 before; array_index_buffer's and
        # wshell_buffer's put_contents_with_key/2 now compile and succeed
        # on both sides.  Step 3e's pmi ca (kl0): 94 / 86 / 40 / 7 before;
        # array_index_buffer's and wshell_buffer's set_all_at/2 and
        # reset_all_at/2 now run the held code too, and agree
        self.assertEqual(dict(self.r['census']), {'same outcome': 98, 'both refused': 86,
                                                  'refused compiled only': 40,
                                                  'refused held only': 3})


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
        # with the step 3c rows: 12,479 compared, 1,485 exact
        # with the step 3d rows: 12,816 compared, 1,513 exact (none lost)
        self.assertEqual((c['pred compared'], c['pred exact']), (12816, 1513))
        self.assertEqual([c['%s agree' % a] for a in ('natures', 'slots', 'methods', 'locals')],
                         [738, 738, 736, 736])
        # internal: 2 before step 3c (the PCM add_to_ele_by_search/10
        # pair); with substring/4 two IXM pic_up_log_data clauses reach the
        # same `temporary ... lost its register` (it is there with the
        # step 3c register fixes reverted too, so not theirs)
        self.assertEqual((r['refusals']['macro rule'], r['refusals']['internal']), (40, 4))
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
            'simpos##alarm_watch', 'simpos##as_class_with_lock', 'simpos##as_message',
            'simpos##as_program',
            'simpos##bounded_channel', 'simpos##bounded_post_queue', 'simpos##channel',
            'simpos##common_network',
            'simpos##e_string', 'simpos##hash_index', 'simpos##list', 'simpos##list_index',
            'simpos##message', 'simpos##name', 'simpos##network_listener_buffer',
            'simpos##pathname', 'simpos##pmacs_window', 'simpos##post_queue',
            'simpos##post_queue_for_message', 'simpos##process', 'simpos##process_clock',
            'simpos##semaphore', 'simpos##standard_editor',
            'simpos##stream', 'simpos##string', 'simpos##symbolizer', 'simpos##time',
            'simpos##trace', 'simpos##waiting_frame', 'simpos##waiting_queue',
            'simpos##with_link', 'simpos##with_lock'])
        # the HELD-SOURCE classes (morphana _simpos/, step 3c) keep the
        # predicates espc refuses; every other stand-in compiles whole
        held = {
            'simpos##e_string': {('string_sort', 3): 'calls a refused local',
                                 ('string_sort', 2): 'calls a refused local',
                                 ('qsort', 3): 'calls a refused local',
                                 ('partition', 4): 'if-then-else ->'},
            'simpos##name': {('sort', 3): 'calls a refused local',
                             ('qsort', 3): 'calls a refused local',
                             ('partition', 4): 'if-then-else ->'},
            'simpos##pathname': {('append_names', 3): 'calls a refused local',
                                 ('set_names', 3): 'built-in set_substring/4'},
        }
        for t in self.ts:
            got = {r[0][:2]: r[1] for r in t.refusals}
            self.assertEqual(got, held.get(t.id, {}), t.id)

    def test_methods_labelled(self):
        # owner's rule (2026-11-24): each stand-in method is labelled
        # PRINTED or INTERPOLATED in the comment block just above it (its
        # first clause: a head indented at most 4, as the files are laid out;
        # a body goal is indented further).  Locals are not methods.  A
        # class carried over from held ICOT source (step 3c) labels each
        # method `HELD-SOURCE: file:line`.
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
                self.assertTrue(any('PRINTED:' in x or 'INTERPOLATED' in x
                                    or re.search(r'HELD-SOURCE: \w+\.esp:\d+', x) for x in block),
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
        # tag_catch/9 (interpolated, :refute) runs the timer's
        # do_on_after/3; with allow_forced_event/1 stood in (2026-11-24,
        # step 3c) it gets through to `01 02` @112, integer/1 on the third
        # argument (row blt 01, step 3c): unbound, it fails; an integer
        # took it on to alarm_watch:create/2, stood in at step 3d
        # (INTERPOLATED), and it now gets through to fep_message_assembler
        # @5b, set_string_element (blt 32) on an unbound argument
        m = self.m
        m.reset()
        recv = K.make_instance(m, cid)
        self.assertFalse(any(True for _ in m.solve_send(recv, 'on_after',
                                                        [K.Var(), K.Var(), K.Var(), recv])))
        m.reset()
        recv = K.make_instance(m, cid)
        with self.assertRaises(K.Refusal) as e:
            any(True for _ in m.solve_send(recv, 'on_after', [K.Var(), K.Var(), 10, recv]))
        self.assertEqual(e.exception.cause, 'unbound argument')
        self.assertIn('set_string_element', e.exception.detail)

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

    def send(self, obj, name, *args):
        m = self.m
        m.reset()
        regs = list(args) + [obj]
        return [[K.resolve(a) for a in args] for _ in m.solve_send(obj, name, regs)]

    def test_channel(self):
        # the printed channel (TM-100 Fig. 3.7): its post_queue slot, code-
        # initialised, overrides stream's code-initialised slot of the same
        # name; create/2 and put/get are the printed stream's
        (c,) = K.call_class_method(self.m, 'simpos##channel', 'create', [K.Var()])
        ch = c[0]
        self.assertEqual([x.cid for x in ch.slots],
                         ['simpos##post_queue_for_message', 'simpos##waiting_queue'])
        self.assertEqual(len(self.send(ch, 'put', K.Atom('m1'))), 1)
        self.assertEqual(len(self.send(ch, 'put', K.Atom('m2'))), 1)
        self.assertEqual(repr(self.send(ch, 'get', K.Var())), '[[m1]]')
        # the printed bounded_channel (Fig. 3.10): a plain `attribute
        # post_queue;` overrides channel's initialiser, and create/3 fills
        # it with the printed bounded_post_queue (Fig. 3.11), whose
        # before-demon on add_object takes a token from the interpolated
        # semaphore and whose after-demon on remove_object gives it back
        (b,) = K.call_class_method(self.m, 'simpos##bounded_channel', 'create', [K.Var(), 2])
        bc = b[0]
        q = bc.slots[0]
        sem = q.slots[0]
        co = self.m.lib.build('simpos##semaphore')
        tokens = {e.name: v for e, v in zip(co.instance_slots, sem.slots)}['tokens']
        self.assertEqual((q.cid, sem.cid, tokens), ('simpos##bounded_post_queue', 'simpos##semaphore', 2))
        self.assertEqual(len(self.send(bc, 'put', K.Atom('a'))), 1)
        self.assertEqual(len(self.send(bc, 'put', K.Atom('b'))), 1)
        self.assertEqual(self.send(bc, 'put', K.Atom('c')), [])
        self.assertEqual(repr(self.send(bc, 'get', K.Var())), '[[a]]')
        self.assertEqual(len(self.send(bc, 'put', K.Atom('c'))), 1)
        self.assertEqual(repr(self.send(bc, 'get', K.Var())), '[[b]]')
        self.assertEqual(repr(self.send(bc, 'get', K.Var())), '[[c]]')

    def index_battery(self, ix):
        a, b, c, k1, k2 = (K.Atom(x) for x in ('a', 'b', 'c', 'k1', 'k2'))
        for o, k in ((a, k1), (b, k2), (c, k1)):
            self.assertEqual(len(self.send(ix, 'add_at', o, k)), 1)
        got = {}
        for sel, args in (('get_at', (K.Var(), k1)), ('get_contents', (K.Var(),)),
                          ('get_contents_with_key', (K.Var(),)), ('get_keys', (K.Var(),)),
                          ('get_contents_at', (K.Var(), k1)), ('remove_at', (K.Var(), k1)),
                          ('get_contents', (K.Var(),)), ('get_at', (K.Var(), k1)),
                          ('remove_at', (K.Var(), k1)), ('remove_at', (K.Var(), k1)),
                          ('get_at', (K.Var(), k2)), ('clear', ()), ('get_contents', (K.Var(),))):
            got.setdefault(sel, []).append(repr(self.send(ix, sel, *args)).replace(' ', ''))
        return got

    def test_list_index(self):
        # the interpolated list_index on the layout kappa2's KPPOOL.ESP and
        # SVHSH_IDX.ESP read: entries {Next,Object,Key} from `first`
        (r,) = K.call_class_method(self.m, 'simpos##list_index', 'create', [K.Var()])
        got = self.index_battery(r[0])
        self.assertEqual(got, {
            'get_at': ['[[a,k1]]', '[[c,k1]]', '[[b,k2]]'],
            'get_contents': ['[[[a,b,c]]]', '[[[b,c]]]', '[[[]]]'],
            'get_contents_with_key': ['[[[{a,k1},{b,k2},{c,k1}]]]'],
            'get_keys': ['[[[k1,k2,k1]]]'],
            'get_contents_at': ['[[[a,c],k1]]'],
            'remove_at': ['[[a,k1]]', '[[c,k1]]', '[]'],
            'clear': ['[[]]']})
        self.assertEqual(repr(r[0].slots[0]), '$$void')

    def test_hash_index(self):
        # the interpolated hash_index: a vector of `size` list_indexes
        # (SVHSH_IDX.ESP); the bucket of a key is OURS (bucket 0)
        (r,) = K.call_class_method(self.m, 'simpos##hash_index', 'create', [K.Var(), 5])
        h = r[0]
        co = self.m.lib.build('simpos##hash_index')
        slots = {e.name: v for e, v in zip(co.instance_slots, h.slots)}
        self.assertEqual((slots['size'], [x.cid for x in slots['vector'].args]),
                         (5, ['simpos##list_index'] * 5))
        got = self.index_battery(h)
        self.assertEqual(got['get_contents'], ['[[[a,b,c]]]', '[[[b,c]]]', '[[[]]]'])
        self.assertEqual(got['get_contents_with_key'], ['[[[{a,k1},{b,k2},{c,k1}]]]'])
        self.assertEqual(got['remove_at'], ['[[a,k1]]', '[[c,k1]]', '[]'])

    def test_process_create(self):
        # the interpolated process create/3 (as pimfep's as_pimos_device
        # process/4 sends it) makes a dormant process whose parent is the
        # calling one; the slot accessors read and set it
        m = self.m
        (s,) = K.call_class_method(m, 'simpos##process', 'self', [K.Var()])
        areas = K.NIL
        for x in reversed(['free', 'default', 'free', 'small']):
            areas = K.Cons(K.Atom(x), areas)
        (r,) = K.call_class_method(m, 'simpos##process', 'create', [K.Var(), areas])
        p = r[0]
        co = m.lib.build('simpos##process')
        got = {e.name: v for e, v in zip(co.instance_slots, p.slots)}
        self.assertEqual((repr(got['status']), got['parent_process']), ('dormant', s[0]))
        self.assertIsNot(p, s[0])
        self.assertEqual(len(self.send(p, 'set_sub_priority', 3)), 1)
        self.assertEqual(self.send(p, 'sub_priority', K.Var()), [[3]])
        self.assertEqual(len(self.send(p, 'allow_forced_event')), 1)
        # pimfep's own process/4 now runs to a solution
        regs = [K.Var(), K.Var(), K.Var(), K.ClassRef('pimfep##pimos_timer')]
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(regs[-1], 'process', regs)))

    def test_get_window(self):
        # the minimal standard_editor: get_window/2 gives the window slot,
        # 0 for an editor made with new/2, as the census makes it (step
        # 3d's pmacs_window:create/3 sets it; test_step3d_window_and_timer)
        cid = 'pimfep##pimos_window_editor'
        cause, detail = self.refusal(self.plain, cid, 'instance', 'get_window/2')
        self.assertIn('ancestors simpos##standard_editor', detail)
        m = self.m
        e = K.make_instance(m, cid)
        self.assertEqual(self.send(e, 'get_window', K.Var()), [[0]])
        cause, detail = self.refusal(m, cid, 'instance', 'show/3')
        self.assertEqual(cause, 'receiver not an object')

    def call(self, cid, sel, args):
        m = self.m
        m.reset()
        return [[repr(K.resolve(a)) for a in r] for r in K.call_class_method(m, cid, sel, args)]

    def test_symbolizer_numbers(self):
        # get_number/3 and get_number_string/3 (INTERPOLATED, step 3c) on
        # integer/1, X+Y and the immediate arithmetic rows
        sy = 'simpos##symbolizer'
        for s, n in (('0', 0), ('42', 42), ('-305', -305), ('1990', 1990)):
            self.assertEqual(self.call(sy, 'get_number', [K.Var(), K.Str(s)]),
                             [[str(n), "string#'%s'" % s]])
            self.assertEqual(self.call(sy, 'get_number_string', [n, K.Var()]),
                             [[str(n), "string#'%s'" % s]])
        for s in ('', '12a', '-'):
            self.assertEqual(self.call(sy, 'get_number', [K.Var(), K.Str(s)]), [])
        # a `.` or a number that is not an integer: not modelled, refused
        for sel, args in (('get_number', [K.Var(), K.Str('3.5')]),
                          ('get_number_string', [K.Atom('x'), K.Var()])):
            with self.assertRaises(K.Refusal) as e:
                self.call(sy, sel, args)
            self.assertIn('symbolizer:float_number/3', e.exception.detail)

    def test_held_source(self):
        # morphana's _simpos/ classes (HELD-SOURCE), on substring/4,
        # search_character/5 and string_tail/3 (step 3c rows)
        nm = 'simpos##name'
        f = K.Str('abc.esp.3')
        for sel, want in (('ident', 'abc'), ('type', 'esp'), ('version', '3'),
                          ('ident_type', 'abc.esp')):
            self.assertEqual(self.call(nm, sel, [f, K.Var()]),
                             [["string#'abc.esp.3'", "string#'%s'" % want]])
        sep = espc.jis_code('>')
        for s, want in (('a>bc>d', "'a',string#'bc',string#'d'"),
                        ('ab>>c', "'ab',string#'',string#'c'"), ('>a', "'',string#'a'")):
            # (the last two have the element at a search's first position)
            self.assertEqual(self.call('simpos##e_string', 'split', [K.Str(s), sep, K.Var()]),
                             [["string#'%s'" % s, str(sep), '[string#%s]' % want]])
        # pathname get_last/4 searches backwards (pathname.esp:53,
        # search_character from End down to 0): the direction is not
        # witnessed, so kl0 refuses rather than guess
        with self.assertRaises(K.Refusal) as e:
            self.call('simpos##pathname', 'get_last', [K.Str('a>b>c'), K.Var(), K.Var()])
        self.assertIn('backwards', e.exception.detail)

    def test_step3d_lock(self):
        # as_class_with_lock (INTERPOLATED from kappa2 LOADER.ESP:133-153):
        # :lock has :unlock as its alternative, so backtracking into it
        # unlocks; locks nest (OURS: a count)
        ts, failed = espc.compile_text('''class lock_driver has
nature as_class_with_lock;
:held(C) :- :lock(C), :locked(C);
:failed_after(C) :- :lock(C), fail;
:nested(C,N) :- :lock(C), :lock(C), :unlock(C), :locked(C), N = C!lock_count;
end.''', 'simpos')
        self.assertFalse(failed)
        lib = K.load_six()
        for t in list(self.ts) + ts:
            lib.add(t)
        m = K.Machine(lib)
        cid = 'simpos##lock_driver'
        c = K.ClassRef(cid)

        def sols(sel, *args):
            m.reset()
            return [[K.resolve(a) for a in args] for _ in m.solve_send(c, sel, list(args) + [c])]
        self.assertEqual(len(sols('held')), 1)
        self.assertEqual(sols('locked'), [])        # held/1's lock undone on backtracking
        self.assertEqual(sols('failed_after'), [])
        self.assertEqual(sols('locked'), [])
        self.assertEqual(sols('nested', K.Var())[0], [1])
        # with_lock, the instance form, brackets fep_device_table's methods
        # (:lock first, a last-call :unlock): add_at/5 now runs to a solution
        m = self.m
        m.reset()
        t = K.make_instance(m, 'pimfep##fep_device_table')
        regs = [K.Var() for _ in range(4)] + [t]
        self.assertTrue(any(True for _ in m.solve_send(t, 'add_at', regs)))
        m.reset()
        t = K.make_instance(m, 'pimfep##fep_device_table')
        self.assertTrue(any(True for _ in m.solve_send(t, 'lock', [t])))
        self.assertTrue(any(True for _ in m.solve_send(t, 'locked', [t])))
        # backtracking into an instance's :lock unlocks it (the alternative
        # clause, INFERENCE from the class form): exhaust lock/1, then the
        # table is no longer locked
        m.reset()
        t = K.make_instance(m, 'pimfep##fep_device_table')
        self.assertEqual(sum(1 for _ in m.solve_send(t, 'lock', [t])), 1)
        self.assertFalse(any(True for _ in m.solve_send(t, 'locked', [t])))

    def test_step3d_message(self):
        # as_message and message (INTERPOLATED from TR-056 p.12 and TM-100
        # Fig. 3.7): pimscsi##cmt, whose natures include simpos##message,
        # keeps a sender and a body
        m = self.m
        msg = K.make_instance(m, 'pimscsi##cmt')
        self.assertEqual(len(self.send(msg, 'set_sender', K.Atom('reply_channel'))), 1)
        self.assertEqual(repr(self.send(msg, 'get_sender', K.Var())), '[[reply_channel]]')
        self.assertEqual(len(self.send(msg, 'set_content', 42)), 1)
        self.assertEqual(repr(self.send(msg, 'get_content', K.Var())), '[[42]]')

    def test_step3d_window_and_timer(self):
        # pmacs_window (minimal): the window and its standard_editor point
        # at each other; the window protocol is not stood in
        m = self.m
        m.reset()
        (r,) = K.call_class_method(m, 'simpos##pmacs_window', 'create', [K.NIL, K.Var()])
        w = r[1]
        (e,) = self.send(w, 'get_editor', K.Var())
        self.assertEqual(self.send(e[0], 'get_window', K.Var()), [[w]])
        cause, detail = self.refusal(m, 'pimfep##pimfep_message_log', 'class', 'dump_log/1')
        self.assertIn('simpos##pmacs_window:activate/1', detail)
        # trace and network_listener_buffer: the pimfep callers run to a
        # solution (no tracer: OURS).  common_network's callers are
        # covered by test_fep_census only
        for cid, sel in (('pimfep##simpos_user_device', 'trace_string_io'),
                         ('pimfep##pimos_login_requester', 'buffer')):
            o = K.make_instance(m, cid)
            n = 1 if sel == 'trace_string_io' else 2
            regs = [K.Var() for _ in range(n - 1)] + [o]
            m.reset()
            self.assertTrue(any(True for _ in m.solve_send(o, sel, regs)), cid)

    def test_step3e_as_program(self):
        # as_program, PRINTED (TM-100 Fig. 3.3), with process's
        # add_program/2, remove_program/2, no_program/1 and die/1
        # (INTERPOLATED from it and TM-100 p11's prose)
        m = self.m
        m.reset()
        (r,) = K.call_class_method(m, 'simpos##as_program', 'create', [K.Var()])
        prog = r[0]
        self.assertEqual(prog.cid, 'simpos##as_program')
        (s,) = K.call_class_method(m, 'simpos##process', 'self', [K.Var()])
        proc = s[0]
        co = m.lib.build('simpos##process')
        k_status = m.lib.slot_number(co, 'instance', 'status')
        stack = proc.slots[m.lib.slot_number(co, 'instance', 'invocation_stack')]

        def contents():
            (c,) = self.send(stack, 'get_contents', K.Var())
            return repr(c[0])
        # the machine's one process is shared with the other tests: its
        # status and stack are put back whatever happens here
        saved = proc.slots[k_status]
        try:
            proc.slots[k_status] = K.Atom('ready')
            self.assertEqual(len(self.send(prog, 'assign')), 1)
            self.assertEqual((contents(), proc.slots[k_status]), ('[<simpos##as_program>]', K.Atom('ready')))
            # resign_core pops and leaves the process alive; resign on the
            # root program pops and kills it ("nil(=dead)")
            self.assertEqual(len(self.send(prog, 'resign_core')), 1)
            self.assertEqual((contents(), proc.slots[k_status]), ('[]', K.Atom('ready')))
            self.assertEqual(len(self.send(prog, 'invoke')), 1)
            self.assertEqual((contents(), proc.slots[k_status]), ('[]', K.Atom('nil')))
        finally:
            proc.slots[k_status] = saved
            self.send(stack, 'clear')
        # a held class inherits create/2: an instance of itself
        (r,) = K.call_class_method(m, 'pimfep##pimos_timer', 'create', [K.Var()])
        self.assertEqual(r[0].cid, 'pimfep##pimos_timer')
        # a demon-only combination with a stand-in ancestor stays SIMPOS:
        # the stand-in is part of the lost class (kl0, step 3e)
        cause, detail = self.refusal(m, 'pimfep##pimos_window_editor', 'instance', 'carriage_return/1')
        self.assertEqual(cause, 'simpos')
        self.assertIn('stand-in ancestors simpos##standard_editor simpos##as_program', detail)

    def test_fep_census(self):
        # kl0's census of pimfep and pimscsi (stand-ins loaded), 2026-11-24.
        # Before slot initialisation by code ran: 1,215 methods, 486
        # success, 50 failure, 679 refused (195 'slot init by code').
        # After it: 1,228, 501, 50, 677.  After the string built-ins
        # (blt 0b, 1c, 23, 2b), :refute and tag_catch: 515 success (14
        # methods that stopped at new_string/3), 51 failure (packet32
        # is_used/1, no longer refused), 662 refused.  After step 3c's
        # stand-ins (channel, list_index, hash_index, process create/3 and
        # the rest, standard_editor): 1,229 (pimos_window_editor's
        # get_window/2 is now a method), 605 success, 63 failure (12 that
        # refused now fail on an empty index or queue), 561 refused.  After
        # step 3c's rows (blt 01 integer, 06 stack_vector, 10, 16, 32, 33,
        # 40, 5c, 68) and the HELD-SOURCE classes: 607 success (packet and
        # packet32 get_message/2 through substring/4), 101 failure (38 that
        # refused now fail: the census's unbound arguments meet integer/1
        # or stack_vector/2, which fail on them), 521 refused.  Step 3d's
        # rows (blt 6e, 34, pmi b0, b4) left the totals alone (93 refused
        # methods stop later).  Step 3d's ten INTERPOLATED stand-ins
        # (as_class_with_lock, with_lock, as_message, message, trace,
        # common_network, network_listener_buffer, alarm_watch, time,
        # pmacs_window): 1,265 (36 inherited lock/unlock/locked methods,
        # 32 success, 4 locked/1 failure), 665 success (26 that refused),
        # 113 failure (8 that refused: tables empty after lock/1), 487
        # refused; no method moved out of success.  Step 3e's pmi ca: 666
        # success (remote_pimfep_executor check_status/3), 486 refused; 22
        # more refused methods stop later.  Step 3e's blt f2: 667 success
        # (pimos_window_editor abort_getl/1, cmt show_status/1), 120
        # failure (6 that refused), 478 refused; pimos_remote_login_
        # socket_table locked/1 moved from success to failure: add_at/3,
        # which runs before it, used to refuse at f2 with the table still
        # locked, and now fails and unlocks it (locked/1 fails on a fresh
        # machine with or without f2, like the other tables' locked/1).
        # Step 3e's PRINTED as_program, process's interpolated program
        # stack, and kl0's rule that a missing primary under a stand-in
        # ancestor stays SIMPOS: 1,403 methods (138 inherited: create/2,
        # assign/1, invoke/1, resign/1, resign_core/1: create/2 in 26 classes, the others in 28),
        # 782 success (109 of the new ones, and 6 create methods that
        # stopped at create/2), 121 failure (pimos_timer resign_core/1 on
        # the shared process's empty stack), 500 refused; no method left
        # success.
        rows = K.census_fep(K.fep_machine())
        out = {}
        for r in rows:
            out[r[3]] = out.get(r[3], 0) + 1
        self.assertEqual((len(rows), out), (1403, {'success': 782, 'failure': 121, 'refused': 500}))
        self.assertNotIn('slot init by code', {r[4] for r in rows})


if __name__ == '__main__':
    unittest.main()
