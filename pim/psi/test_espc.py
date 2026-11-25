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
   SIMPOS; the FEP census pinned (1,403 methods, 782 success).  Then
   (test_step3e_node_and_editor) the interpolated network_node_name and
   pmacs_window's {editor, Class} option and activity slot; the FEP
   census pinned again (787 success, 16 exception).  Injected into the
   stand-ins from a backup copy, observed: node_name/2 answering 0, the
   option's atom misspelt, each fails only test_step3e_node_and_editor;
   the activity slot removed, or the unbound-options guard removed, each
   errors test_step3e_node_and_editor and fails test_fep_census.
12. Step 3f (2026-11-25, test_step3f_census_recipes): census receivers
   made by their held creators (kl0 RECIPES, OURS): the device creators
   stopped before activate/2, pimos_window's create_pimos_window/3 and
   its editor, remote_pimfep_executor through :new (its after-demon);
   the recipe census pinned (791 / 154 / 441 / 16 / 1, 101 slot
   constants) and the plain census unchanged (test_fep_census).
   Injected into kl0.py from a backup copy (session inject.py, restored
   by cp, cmp-checked), observed, test_kl0.py passing each time: the
   pimos_timer recipe dropped, errors (census slot constants 101 -> 105,
   the timer's goal/1, attention/1, loop_main/1, invoke/1); A0 left
   unbound, fails; no stop before activate/2, errors (the creator
   reaches process:status/3); the executor made by make_instance, fails.
   Each touches only test_step3f_census_recipes.  Re-run 2026-11-25
   against the tightened executor check (accept the string
   'pimos_scsi_fep_control', time 10; both are 0 from make_instance):
   test_step3f_census_recipes fails, nothing else.
   Then (test_step3f_library_and_symbolizer) kl0's library and
   symbolizer models and the string-I/O recipe; census pins 790 / 442
   plain, 792 / 440 and 85 slot constants with recipes.  Injected into
   kl0.py the same way, observed: assign/1 failing, fails
   test_fep_census, test_step3f_census_recipes and
   test_step3f_library_and_symbolizer; the own-package rule dropped,
   fails test_step3f_census_recipes and errors
   test_step3f_library_and_symbolizer; template_file succeeding, fails
   both step 3f tests; enter_atom reading its first argument as the
   string, fails test_step3f_census_recipes and errors
   test_step3f_library_and_symbolizer.  test_kl0.py passes each time.
   Then (test_step3f_window_protocol) pmacs_window's interpolated
   geometry, title and display methods; FEP census 1,420 methods (17 new,
   inherited by pimos_window), 807 / 442 plain and 809 / 440, 86 slot
   constants with recipes.  Injected into standin/pmacs_window.esp the
   same way, observed: get_position/3 answering y, x, fails only
   test_step3f_window_protocol; reshape/5 not setting the size, the
   same; activate/1 failing, fails test_fep_census,
   test_step3d_window_and_timer, test_step3f_census_recipes and
   test_step3f_window_protocol.  test_kl0.py passes each time.
13. Step 3g (2026-11-25, test_step3g_stream_see): stream see/2,
   try_to_see/2 and try_to_get/2 (INTERPOLATED, standin/stream.esp) and
   kl0's 'would suspend' refusal of process:suspend/2 (one process, no
   scheduler); a timer's loop_main/1 with one message on its input
   stream sees it, gets it and stops at blt 6f in disassemble/3.  The
   17 recipe-census rows that stopped at stream:see/2 now refuse 'would
   suspend' (test_step3f_census_recipes); the totals are unchanged.
   Injected from a backup copy, restored by cp, cmp-checked, observed
   (test_kl0.py passing each time): see/2 taking the object out
   (remove_object for see_object), fails only test_step3g_stream_see;
   try_to_see/2 waiting as see/2 does, errors only
   test_step3g_stream_see; try_to_get/2 leaving the object
   (see_object for remove_object), fails only test_step3g_stream_see;
   kl0's suspend/2 model removed (the printed body runs and fails),
   fails test_step3f_census_recipes, test_step3g_stream_see and
   test_stream_runs.
14. Step 3g (2026-11-25, test_step3g_requests): census requests (kl0
   REQUEST_ID = 16, request_args, COMMAND_RECEIVERS, ABORT_HANDLERS;
   the creators' device-id and output-stream positions read per
   creator, which corrects step 3f's pimos_file recipe).  Recipe census
   829 / 152 / 422, 96 slot constants (test_step3f_census_recipes).
   Injected into kl0.py from a backup copy, restored by cp,
   cmp-checked, observed (test_kl0.py passing each time unless said):
   the creators' device id left unbound: test_step3g_requests errors,
   test_step3f_census_recipes fails; pimos_file's stream back in A0
   with no open mode: test_step3f_census_recipes errors; the
   command-receiver check dropped (pimos_window's get_position/3 given
   a request): test_step3f_census_recipes and test_step3g_requests
   fail; blt 48 R != A refused again: test_step3f_census_recipes fails,
   and in test_kl0.py test_result_register errors and test_census
   fails.
15. Step 3g (2026-11-25): pmi c6/ce/c3/c1/ff and tables cd03/cd04
   (test_kl0.py Step3gSwitches, which lists the injections): plain FEP
   census 808 / 163 / 432, recipes 831 / 161 / 411.  ce's key length
   N - 1 and ff's target cell + 3 each fail test_fep_census and
   test_step3f_census_recipes here.
16. Step 3g (2026-11-25, test_step3g_invocation_stack): process
   invocation_stack/2 (INTERPOLATED).  Injected into standin/process.esp
   from a backup, restored by cp, cmp-checked, observed: answering a new
   empty list fails test_step3g_invocation_stack, test_fep_census and
   test_step3f_census_recipes; test_kl0.py passes.

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
  - source check (2026-11-25, observed): standin/pathname.esp put back
    to its committed text (`remove_or_local/6`), restored by cp from a
    backup and cmp-checked: only test_source_check_labels fails.
  - string identity (2026-11-25): the four injections (unify and ==
    by content again, equal_key/2 as unification, string/3 refusing a
    non-string) and what each fails in both files are in test_kl0.py's
    header.
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
            'simpos##alarm_watch', 'simpos##as_boot_program', 'simpos##as_class_with_lock',
            'simpos##as_message', 'simpos##as_program', 'simpos##boot_process',
            'simpos##bounded_channel', 'simpos##bounded_post_queue', 'simpos##channel',
            'simpos##common_network',
            'simpos##e_string', 'simpos##hash_index', 'simpos##list', 'simpos##list_index',
            'simpos##message', 'simpos##name', 'simpos##network_listener_buffer',
            'simpos##network_node_name',
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

    def test_source_check_labels(self):
        # docs/simpos/source_check_2026-11-24.md §5, applied 2026-11-25:
        # each corrected statement is pinned, and each stale one is absent.
        def text(name):
            with open(os.path.join(espc.STANDIN, name + '.esp')) as f:
                return f.read()
        must = {
            'time': ['MILLISECONDS', 'CH_CLOCK.ESP:60'],                 # P-s15
            'pathname': ['remote_or_local/6'],                            # P-s7
            'semaphore': ['no body of\n% TM-100', 'TR-056 p11 (PDF p13)'],  # P-s1
            'message': ['PRINTED (prose): TR-056 PDF p14'],               # P-s14
            'with_lock': ['functions.esp:763-836'],                       # P-s13
            'list_index': ['equal_key'],                                  # P-s2
            'trace': ['autoTracer.esp:23'],                               # P-s16
        }
        never = {
            'pathname': ['remove_or_local'],
            'stream': ['no stand-in yet'],
            'message': ['no part of\n% `message` is printed'],
            'as_message': ['no part of\n% `as_message` is printed'],
        }
        for name, xs in must.items():
            for x in xs:
                self.assertIn(x, text(name), name)
        for name, xs in never.items():
            for x in xs:
                self.assertNotIn(x, text(name), name)

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
        # the printed put/2 and get/2: first in, first out.  get on an
        # empty stream reaches process:suspend/2, which kl0 refuses since
        # step 3g ('would suspend': one process, no scheduler); before, the
        # printed suspend/2 failed for the census's process (status nil)
        # and the wait showed as a clean failure
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
        with self.assertRaises(K.Refusal) as cm:
            send('get', K.Var())
        self.assertEqual(cm.exception.cause, 'would suspend')

    def test_printed_process_slots(self):
        # :self(#process,P) makes the process with :new, which runs the
        # printed slot initialisers (TM-100 Fig. 3.1): four lists and a clock.
        # Since step 3i the first process is the boot process (a
        # boot_process, no slots of its own), activated: status `active`
        (a,) = K.call_class_method(self.m, 'simpos##process', 'self', [K.Var()])
        self.assertEqual(a[0].cid, 'simpos##boot_process')
        co = self.m.lib.build('simpos##process')
        self.assertEqual(len(co.instance_slots), len(self.m.lib.build('simpos##boot_process').instance_slots))
        got = {e.name: v for e, v in zip(co.instance_slots, a[0].slots)}
        for n in ('suspend_reasons', 'children_processes', 'invocation_stack', 'resources'):
            self.assertEqual(got[n].cid, 'simpos##list', n)
        self.assertEqual(got['clock'].cid, 'simpos##process_clock')
        self.assertEqual((got['mask_count'], repr(got['status'])), (0, 'active'))
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

    def test_string_keys(self):
        # strings unify only by storage (TM-388 PDF p79), so list_index's
        # equal_key/2 compares string keys by contents, as held callers need
        # (p_wshell.esp:102/:396 set and read "$from" with two literals);
        # other keys still by unification.  Each key below is a distinct
        # Str with the same contents as the one added.
        for cid, args in (('simpos##list_index', [K.Var()]), ('simpos##hash_index', [K.Var(), 3])):
            (r,) = K.call_class_method(self.m, cid, 'create', args)
            ix = r[0]
            R = lambda x: repr(x).replace(' ', '')
            self.assertEqual(len(self.send(ix, 'add_at', K.Atom('v1'), K.Str('$from'))), 1)
            self.assertEqual(len(self.send(ix, 'add_at', K.Atom('v2'), K.Atom('k'))), 1)
            self.assertEqual(R(self.send(ix, 'get_at', K.Var(), K.Str('$from'))), '[[v1,string#\'$from\']]', cid)
            self.assertEqual(self.send(ix, 'get_at', K.Var(), K.Str('$fro')), [], cid)
            self.assertEqual(R(self.send(ix, 'get_contents_at', K.Var(), K.Str('$from'))),
                             '[[[v1],string#\'$from\']]', cid)
            self.assertEqual(R(self.send(ix, 'get_at', K.Var(), K.Atom('k'))), '[[v2,k]]', cid)
            self.assertEqual(R(self.send(ix, 'remove_at', K.Var(), K.Str('$from'))),
                             '[[v1,string#\'$from\']]', cid)
            self.assertEqual(self.send(ix, 'get_at', K.Var(), K.Str('$from')), [], cid)

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
        self.assertEqual(cause, 'receiver a slot constant')

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
        # step 3f: activate/1 is stood in; the text output (window.md
        # §2.4, putl/2) is not
        self.assertIn('simpos##pmacs_window:putl/2', detail)
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

    def test_step3e_node_and_editor(self):
        # network_node_name (INTERPOLATED): both selectors give the one
        # name, OURS "psi"; fep_node_table's initiate/1 stores it
        m = self.m
        for sel in ('get_my_node', 'node_name'):
            m.reset()
            self.assertEqual(repr(K.call_class_method(m, 'simpos##network_node_name', sel, [K.Var()])),
                             "[[string#'psi']]", sel)
        o = K.make_instance(m, 'pimfep##fep_node_table')
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(o, 'initiate', [o])))
        # pmacs_window's {editor, Class} option (step 3e): pimos_window's
        # create_pimos_window/3 makes a window whose editor is a
        # pimos_window_editor, and sets its activity slot to 1; without
        # the option the editor is a standard_editor and activity 0
        m.reset()
        (r,) = K.call_class_method(m, 'pimfep##pimos_window', 'create_pimos_window', [K.Var(), K.Var()])
        w = r[1]
        co = m.lib.build(w.cid)
        s = {e.name: v for e, v in zip(co.instance_slots, w.slots)}
        self.assertEqual((s['editor'].cid, s['activity']), ('pimfep##pimos_window_editor', 1))
        self.assertEqual(self.send(s['editor'], 'get_window', K.Var()), [[w]])
        m.reset()
        (r,) = K.call_class_method(m, 'simpos##pmacs_window', 'create', [K.Var(), K.Var()])
        co = m.lib.build(r[1].cid)
        s = {e.name: v for e, v in zip(co.instance_slots, r[1].slots)}
        self.assertEqual((s['editor'].cid, s['activity']), ('simpos##standard_editor', 0))

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
        # success.  Step 3e's rows blt 9a/9b, pmi b1/b5/b6/b7, blt 50/51/
        # 54/55 and R != A for blt 40/49: 784 success (pimfep_message_log
        # log/2, cmt make_CDB/3), 123 failure (as_pimos_string_io_device
        # and pimos_remote_login_replier io/5, which refused at b1), 496
        # refused (32 more stop later); no method left success.  Step
        # 3e's census outcome 'exception': the 16 sends of
        # :raise(#undefined_method, ...) (scsi_low_if's class reset/
        # initialize/shutdown, unless overridden) leave refused, 480 refused.
        # The 139 sends to an integer still holding its slot's template
        # constant are refused as 'receiver a slot constant', not 'receiver
        # not an object' (14 remain: atoms none, nil).
        # Step 3e's stand-ins network_node_name and pmacs_window's
        # {editor, Class} option and activity slot: 787 success
        # (fep_node_table initiate/1, local_node_name/2, pimos_window
        # create_pimos_window/3), 477 refused (13 more stop later); no
        # method left success.  2026-11-25: blt 19 V != N witnessed
        # (FMT_CONV.ESP:13-16): packet32 initiate/1 goes on from its
        # new_heap_vector and runs into the step limit (476 refused).
        # 2026-11-25: strings unify by storage only (no row moves: the
        # census's arguments are unbound) and string/3 is a type test
        # that fails on a non-string: 33 methods leave refused (30 to
        # failure, 3 to success), 6 stop later (3 at a missing opcode, 3
        # at a slot constant), and pimos_file resign_core/1 leaves success
        # (a census order effect: alone, on a fresh machine, it fails
        # before and after).
        # 2026-11-25, step 3f: the library (assign/1, check_info/3,
        # get_class_object/3) and symbolizer enter_atom/3 models: 11
        # refused methods stop later, remote_stream create_to_fep/3 leaves
        # refused for success, create_from_fep/4 stops at an unbound
        # receiver; none leaves success.
        # 2026-11-25, step 3f: pmacs_window's geometry, title, font and
        # display methods (INTERPOLATED): 17 new methods, inherited by
        # pimos_window, all succeed; 3 pimfep_message_log rows stop later.
        rows = K.census_fep(K.fep_machine())
        out = {}
        for r in rows:
            out[r[3]] = out.get(r[3], 0) + 1
        # 2026-11-25, step 3g: pmi c6/ce/c3/c1/ff witnessed (RDMSOPE.ESP,
        # p_MAIN.esp, receiver.esp): 808 / 163 / 432 (login_server
        # device_abort/1 succeeds, checked alone; nine pimscsi methods fail
        # on the census's unbound first argument, as in the recipe census)
        # 2026-11-25, step 3h: pmi 34/35 witnessed (receiver.esp:669, :680):
        # 808 / 165 / 430.  Two rows leave refused for failure, both on the
        # census's unbound arguments (net_spawn_user take_ip_address/3 in
        # the e_string stand-in, scsi receive_command/3 at check_argument's
        # `string` clause, blt 0b on an unbound); two scsi_device rows stop
        # later, at an unbound receiver.  Not progress
        # step 3h: blt e1 witnessed (p_what.esp:88, g_window.esp:147):
        # 808 / 165 / 430 -> 809 / 165 / 429.  pimos_fep_initiation_table
        # set_scsi_init_list/2 succeeds (checked alone: the census's unbound
        # list becomes four non-integers, each stored as nil; unbound
        # probing, not progress); six rows stop later
        # step 3h: process:children/2 (INTERPOLATED): pimos_scsi_front_end
        # exit/1 succeeds (809 -> 810, 429 -> 428).  Checked alone: on the
        # census's front end fep_type is the template constant 0 (create/6
        # writes it, @50), so the shutdown branch is skipped, and the
        # census's process has no children.  A census artifact, not progress
        # step 3i: every row from freshly generated class objects (kl0
        # census_of; test_step3i_census_order): 810 / 165 / 428 -> 757 /
        # 219 / 427.  70 rows move, all order effects (each checked alone
        # on a new machine, psi/README.md "Step 3i"): 54 resign/1 and
        # resign_core/1 rows fail on the row's own empty program stack;
        # two locked/1 fail unlocked; pseudo_scsi shutdown/1 and three
        # remote_login_replier rows refuse; create_socket/9 fails (no
        # program on its process's stack); four pimfep_message_log rows
        # succeed on the empty log (`none`), not progress
        self.assertEqual((len(rows), out), (1420, {'success': 757, 'failure': 219, 'refused': 427, 'exception': 16,
                                                   'step limit': 1}))
        self.assertNotIn('slot init by code', {r[4] for r in rows})

    def test_step3f_census_recipes(self):
        # step 3f: receivers made by their held creators (kl0 RECIPES, OURS)
        m = K.fep_machine()
        # pimos_timer create_timer/9 stopped before activate/2: the device
        # has the two streams its creator made with stream/2 and the output
        # stream the recipe passed; device_id is REQUEST_ID, the A3 the
        # recipe passes since step 3g (unbound before)
        dev = K.RECIPES['pimfep##pimos_timer'](m)
        co = m.lib.build(dev.cid)
        s = {e.name.split('$')[-1]: K.deref(v) for e, v in zip(co.instance_slots, dev.slots)}
        self.assertEqual([getattr(s[n], 'cid', s[n]) for n in
                          ('input_stream', 'output_stream', 'creation_status_stream')],
                         ['simpos##stream'] * 3)
        self.assertIsNot(s['input_stream'], s['creation_status_stream'])
        self.assertEqual(s['device_id'], K.REQUEST_ID)
        # pimos_file (step 3g): the stream is the output stream (A1, as
        # read_open/10 shifts the message), the open mode `read`, the id 16
        f = K.RECIPES['pimfep##pimos_file'](m)
        co = m.lib.build(f.cid)
        s = {e.name.split('$')[-1]: K.deref(v) for e, v in zip(co.instance_slots, f.slots)}
        self.assertEqual((s['output_stream'].cid, s['open_mode'], s['device_id']),
                         ('simpos##stream', K.Atom('read'), 16))
        # the window's editor points back at it
        ed = K.RECIPES['pimfep##pimos_window_editor'](m)
        self.assertEqual(ed.cid, 'pimfep##pimos_window_editor')
        # remote_pimfep_executor through :new, so its after-demon on new/2
        # copies the class slot socket into accept: that slot's own
        # template constant, a string (one template constant for another)
        ex = K.RECIPES['pimfep##remote_pimfep_executor'](m)
        co = m.lib.build(ex.cid)
        s = {e.name: K.deref(v) for e, v in zip(co.instance_slots, ex.slots)}
        self.assertIsInstance(s['accept'], K.Str)
        self.assertEqual(s['accept'].text, 'pimos_scsi_fep_control')
        self.assertEqual(s['time'], 10)
        rows = K.census_fep(K.fep_machine(), recipes=K.RECIPES)
        by = {(r[0].split('##')[1], r[1], r[2]): r[3:] for r in rows}
        out = {}
        for r in rows:
            out[r[3]] = out.get(r[3], 0) + 1
        # step 3g: the requests (REQUEST_ID and the command's code) and
        # pimos_file's corrected recipe: 809 / 154 / 440 -> 829 / 152 / 422;
        # 10 editor replies reach the unset window process (slot
        # constants 86 -> 96)
        # step 3g: pmi c6/ce/c3/c1/ff and tables cd03/cd04 witnessed: 829 /
        # 152 / 422 -> 831 / 161 / 411.  The two successes (login_server
        # device_abort/1, abort_string_io/2) were checked alone on a fresh
        # machine; the nine failures (pimscsi cmt, scsi, scsi_communicator
        # check_argument/2, low_if/2, send_request/5, receive_request/5)
        # are not progress.  Step 3h traced the six low_if/send_request/
        # receive_request rows (test_step3h_scsi_mode): initiator methods
        # on a receiver in target mode (lun 0, an integer), held behaviour
        # step 3h: pmi 34/35 witnessed: 831 / 163 / 409 (the same four rows
        # as the plain census move)
        # step 3h: blt e1 witnessed: 831 / 163 / 409 -> 832 / 163 / 408 (the
        # same seven rows as the plain census)
        # step 3h: process:children/2: the same row, 833 / 163 / 407.
        # step 3h: pimos_tcpip_socket's recipe: 836 / 164 / 403, slot
        # constants 96 -> 93.  attention/1, bind/4 and flush/3 succeed
        # (each checked alone: a reply put on the output stream);
        # abort_loop/1 fails (try_to_see/2 on the empty input stream);
        # loop_main/1 waits in see/2 ('would suspend')
        # step 3i: every row from freshly generated class objects: 836 /
        # 164 / 403 -> 782 / 220 / 401, the same order effects as the
        # plain census (55 resign rows here, two remote_login_replier);
        # slot constants 93 -> 94 (pseudo_scsi_handler send_to_PE/2, which
        # met an earlier row's unbound value before)
        self.assertEqual((len(rows), out), (1420, {'success': 782, 'failure': 220, 'refused': 401,
                                                   'exception': 16, 'step limit': 1}))
        slot_const = sum(1 for r in rows if r[4] == 'receiver a slot constant')
        self.assertEqual(slot_const, 94)
        self.assertEqual(by[('pimos_tcpip_socket', 'instance', 'loop_main/1')][:2], ('refused', 'would suspend'))
        self.assertEqual(by[('pimos_tcpip_socket', 'instance', 'bind/4')][0], 'success')
        # the four string-I/O programs, made by create_string_io/10
        # step 3g: a device's loop_main/1 waits in stream see/2 on its
        # empty input stream ('would suspend'), as do the 17 goal/1,
        # loop_main/1 and invoke/1 rows that stopped at see/2 before
        for c in K.STRING_IO_PROGRAMS:
            self.assertEqual(by[(c.split('##')[1], 'instance', 'loop_main/1')][:2],
                             ('refused', 'would suspend'), c)
        self.assertEqual(by[('as_pimos_string_io_device', 'instance', 'loop_main/1')][:2],
                         ('refused', 'receiver a slot constant'))
        # a device with a recipe goes on to the wait in see/2; the
        # abstract as_pimos_device (no creator) still refuses
        self.assertEqual(by[('pimos_timer', 'instance', 'loop_main/1')][:2],
                         ('refused', 'would suspend'))
        self.assertIn('stream', by[('pimos_timer', 'instance', 'loop_main/1')][2])
        # 17, and since step 3h pimos_tcpip_socket loop_main/1: 18
        self.assertEqual(sum(1 for r in rows if r[4] == 'would suspend'), 18)
        self.assertNotIn('simpos##stream:see/2', {K.simpos_target(r[5]) for r in rows})
        self.assertEqual(by[('as_pimos_device', 'instance', 'loop_main/1')][:2],
                         ('refused', 'receiver a slot constant'))
        # pimos_file: with the open mode `read` (step 3g), initiate/1 and
        # goal/1 reach the SIMPOS directory (step 3f's failure and
        # success were on a stream in the open-mode argument)
        for sel in ('initiate/1', 'goal/1'):
            self.assertEqual(by[('pimos_file', 'instance', sel)][:2], ('refused', 'simpos'))
            self.assertIn('simpos##directory:retrieve/3', by[('pimos_file', 'instance', sel)][2])
        # step 3g: the device replies to the request REQUEST_ID
        for c in ('pimos_timer', 'pimos_directory', 'pimos_window_process', 'pimos_file',
                  'simpos_user_device', 'pimos_remote_login_replier', 'pimos_standard_io_window',
                  'pimos_remote_login_server'):
            self.assertEqual(by[(c, 'instance', 'attention/1')][0], 'success', c)
        self.assertEqual(by[('pimos_timer', 'instance', 'close/3')][0], 'success')
        self.assertEqual(by[('pimos_timer', 'instance', 'abort_timer/3')][0], 'success')
        # the editor reaches pimos_window's lost pmacs_window protocol
        # (get_interpreter/2 is not stood in)
        self.assertIn('pimfep##pimos_window:get_interpreter/2',
                      by[('pimos_window_editor', 'instance', 'clear/3')][2])
        # with the interpolated geometry and title (step 3f), get_title/3
        # runs through the window to its reply; with the request (step 3g)
        # and blt 48 R != A, the reply's assembly stops at blt 36;
        # set_size/3 at the has_been_reshaped/1 callback
        self.assertEqual(by[('pimos_window_editor', 'instance', 'get_title/3')][:2],
                         ('refused', 'opcode'))
        self.assertIn('blt 36', by[('pimos_window_editor', 'instance', 'get_title/3')][2])
        self.assertIn('has_been_reshaped/1', by[('pimos_window_editor', 'instance', 'set_size/3')][2])
        self.assertEqual(by[('pimos_window', 'instance', 'set_output_stream/2')][0], 'success')

    def test_step3g_stream_see(self):
        # stream see/2, try_to_see/2, try_to_get/2 (step 3g, INTERPOLATED
        # from their held callers; standin/stream.esp)
        m = self.m
        m.reset()
        (s,) = K.call_class_method(m, 'simpos##stream', 'create', [K.Var()])
        st = s[0]

        def send(name, *args):
            m.reset()
            regs = list(args) + [st]
            return [[K.resolve(a) for a in args] for _ in m.solve_send(st, name, regs)]
        # empty: try_to_see and try_to_get fail at once; see/2 would wait
        self.assertEqual(send('try_to_see', K.Var()), [])
        self.assertEqual(send('try_to_get', K.Var()), [])
        with self.assertRaises(K.Refusal) as cm:
            send('see', K.Var())
        self.assertEqual(cm.exception.cause, 'would suspend')
        send('put', K.Atom('a'))
        send('put', K.Atom('b'))
        # see/2 and try_to_see/2 give the oldest object and leave it
        self.assertEqual(repr(send('see', K.Var())), '[[a]]')
        self.assertEqual(repr(send('try_to_see', K.Var())), '[[a]]')
        self.assertEqual(repr(send('see', K.Var())), '[[a]]')
        # try_to_get/2 takes it out; then see/2 gives the next
        self.assertEqual(repr(send('try_to_get', K.Var())), '[[a]]')
        self.assertEqual(repr(send('see', K.Var())), '[[b]]')
        self.assertEqual(repr(send('get', K.Var())), '[[b]]')
        self.assertEqual(send('try_to_see', K.Var()), [])
        # a timer made by its creator, with one message on its input
        # stream: loop_main/1 sees it, gets it (the stream is empty after)
        # and goes on to its local refute/3, which stops at
        # fep_message_assembler disassemble/3's unwitnessed blt 6f
        dev = K.RECIPES['pimfep##pimos_timer'](m)
        co = m.lib.build(dev.cid)
        sl = {e.name.split('$')[-1]: K.deref(v) for e, v in zip(co.instance_slots, dev.slots)}
        inp = sl['input_stream']
        msg = K.Str('', 32)
        msg.set_codes([16, 0, 60, 0])
        m.reset()
        self.assertEqual(len(list(m.solve_send(inp, 'put', [msg, inp]))), 1)
        m.reset()
        with self.assertRaises(K.Refusal) as cm:
            any(True for _ in m.solve_send(dev, 'loop_main', [dev]))
        self.assertEqual(cm.exception.cause, 'opcode')
        self.assertIn('blt 6f', cm.exception.detail)
        self.assertEqual(repr(K.resolve(inp.slots[0].slots[0])), '[]')

    def test_step3g_requests(self):
        # step 3g: census requests (kl0 REQUEST_ID, request_args, OURS
        # values in held-code positions).  A command handler of a class
        # with a recipe gets [Id, Code], the code from the held
        # fep_command_code_table convert/3; an abort handler [Id]; a
        # method of a class that receives no commands, nothing
        m = K.fep_machine()
        self.assertEqual(K.request_args(m, 'pimfep##pimos_timer', 'close', 3), [16, 60])
        self.assertEqual(K.request_args(m, 'pimfep##pimos_window_editor', 'get_title', 3), [16, 131])
        self.assertEqual(K.request_args(m, 'pimfep##simpos_user_device', 'abort_string_io', 2), [16])
        self.assertEqual(K.request_args(m, 'pimfep##pimos_window', 'get_position', 3), [])
        self.assertEqual(K.request_args(m, 'pimfep##pimos_timer', 'attention', 1), [])

        def replies(name, n):
            dev = K.RECIPES['pimfep##pimos_timer'](m)
            co = m.lib.build(dev.cid)
            sl = {e.name.split('$')[-1]: K.deref(v) for e, v in zip(co.instance_slots, dev.slots)}
            lead = K.request_args(m, dev.cid, name, n)
            regs = lead + [K.Var() for _ in range(n - 1 - len(lead))] + [dev]
            self.assertTrue(any(True for _ in m.solve_send(dev, name, regs)))
            q, out = K.resolve(sl['output_stream'].slots[0].slots[0]), []
            while isinstance(q, K.Cons):
                out.append(K.deref(q.args[0]).codes())
                q = K.deref(q.args[1])
            return out
        # the replies the device puts on its output stream: {Id, Status} as
        # [Id, 0, Status, 0] (get_device_id/3 reads element 0,
        # get_command/3 element 2, disassemble/3 element 3)
        self.assertEqual(replies('attention', 1), [[16, 0, 3, 0]])
        self.assertEqual(replies('close', 3), [[16, 0, 1, 0], [16, 0, 903, 0]])

    def test_step3g_invocation_stack(self):
        # process:invocation_stack/2 (step 3g, INTERPOLATED: TM-100 Fig.
        # 3.1's slot; kappa-p kappaPITR.esp:13-14).  It answers the stack
        # list itself; held pimos_tcpip_socket create_socket/9 then takes
        # the calling program with get_first/2 (@4d-59) and stores it as
        # the device's fep_object before activate/2
        m = self.m
        m.reset()
        (r,) = K.call_class_method(m, 'simpos##as_program', 'create', [K.Var()])
        prog = r[0]
        (s,) = K.call_class_method(m, 'simpos##process', 'self', [K.Var()])
        proc = s[0]
        co = m.lib.build('simpos##process')
        stack = proc.slots[m.lib.slot_number(co, 'instance', 'invocation_stack')]
        cid = 'pimfep##pimos_tcpip_socket'

        def create_socket():
            (st,) = K.call_class_method(m, 'simpos##stream', 'create', [K.Var()])
            args = [K.Var() for _ in range(8)]
            args[0], args[3] = st[0], K.REQUEST_ID
            m.stop_before = {('activate', 2)}
            try:
                return [None for _ in m.solve_send(K.ClassRef(cid), 'create_socket', args + [K.ClassRef(cid)])]
            except K.CreatorStopped as e:
                dev = e.args[2][0]
                dco = m.lib.build(dev.cid)
                return {x.name.split('$')[-1]: K.deref(v) for x, v in zip(dco.instance_slots, dev.slots)}
            finally:
                m.stop_before = None
        # the census's process runs no program: get_first/2 fails on the
        # empty stack, so the creator fails (since step 3h the tcpip recipe
        # pushes a front end first: test_step3h_tcpip_recipe).  The
        # machine is shared: empty the stack first
        self.send(stack, 'clear')
        self.assertEqual(create_socket(), [])
        self.assertEqual(len(self.send(proc, 'add_program', prog)), 1)
        try:
            L = K.Var()
            self.assertEqual([K.resolve(L) is stack for _ in m.solve_send(proc, 'invocation_stack', [L, proc])],
                             [True])
            sl = create_socket()
            self.assertIs(sl['fep_object'], prog)
            self.assertIs(sl['fep_process'], proc)
            self.assertEqual(sl['device_id'], K.REQUEST_ID)
        finally:
            self.send(stack, 'clear')

    def test_step3i_census_order(self):
        # step 3i: each census row starts from freshly generated class
        # objects (kl0 census_of drops the class slots before every call),
        # so a row's outcome does not depend on the rows before it.  The
        # census run backwards (classes and each class's methods in the
        # opposite order) must give the same row, row for row, plain and
        # with recipes.  Variable names are normalised.
        # Injected (2026-11-25) from a backup, restored by cp, cmp-checked.
        # Observed:
        # - the reset line removed: this test, test_fep_census and
        #   test_step3f_census_recipes fail; test_kl0.py passes
        def norm(rows):
            return {r[:3]: (r[3], r[4], re.sub(r'_G\d+', '_G', r[5])) for r in rows}
        for recipes in (None, K.RECIPES):
            m = K.fep_machine()
            classes = [c for c in m.lib.templates if c.split('##')[0] in K.FEP_PACKAGES]
            fwd = norm(K.census_of(m, classes, recipes))
            bwd = norm(K.census_of(K.fep_machine(), classes, recipes, reverse=True))
            self.assertEqual(len(fwd), 1420)
            diff = sorted(k for k in fwd if fwd[k] != bwd.get(k))
            self.assertEqual(diff, [], recipes is not None)
        # the order effect step 3h left open: set_log_table/2's unbound
        # argument no longer reaches dump_log/1, which goes on to the
        # message window (pmacs_window putl/2, not stood in)
        by = norm(K.census_fep(K.fep_machine()))
        self.assertEqual(by[('pimfep##pimfep_message_log', 'class', 'dump_log/1')][:2],
                         ('refused', 'simpos'))
        self.assertIn('pmacs_window:putl/2', by[('pimfep##pimfep_message_log', 'class', 'dump_log/1')][2])

    def test_step3i_boot(self):
        # step 3i, docs/simpos/boot_route.md B2: the boot process (TM-100
        # p6, p13; TR-056 p21; held pimmcsp##pseudo_pe_process release/1)
        # runs a boot program (as_boot_program, TM-100 p13) with the
        # printed as_program invoke/1.  boot_probe is an OURS test class.
        # Injections, observed (2026-11-25; inject from a backup, restore
        # by copy, cmp clean; test_kl0.py stayed OK in all three):
        #   I1 process.esp self/2 back to :new(Class, P): this test ERROR,
        #      test_printed_process_slots FAIL, nothing else.
        #   I2 the three boot_process_override SIMPOS_MODELS rows deleted:
        #      this test FAIL, nothing else.
        #   I3 the dispatch inheritance walk disabled (models keyed on
        #      simpos##process no longer reach boot_process): this test
        #      passes; test_step3f_census_recipes, test_step3g_stream_see
        #      and test_stream_runs FAIL (the suspend/2 model is inherited).
        ts, failed = espc.compile_text('''class boot_probe has
nature as_boot_program;
instance
attribute seen_p, seen_b, seen_top, seen_status;
:goal(Prog) :- :self(#process, P), :get_instance(#boot_process, B),
    :invocation_stack(P, S), :get_first(S, Top),
    Prog!seen_p := P, Prog!seen_b := B, Prog!seen_top := Top,
    Prog!seen_status := P!status;
end.''', 'simpos')
        self.assertFalse(failed)
        lib = K.load_six()
        for t in list(self.ts) + ts:
            lib.add(t)
        m = K.Machine(lib)
        probe = K.ClassRef('simpos##boot_probe')
        boot = K.ClassRef('simpos##boot_process')

        def one(recv, sel, *args):
            m.reset()
            sols = [[K.deref(a) for a in args] for _ in m.solve_send(recv, sel, list(args) + [recv])]
            self.assertEqual(len(sols[:1]), 1, sel)
            return sols[0]
        (prog,) = one(probe, 'create', K.Var())          # printed as_program create/2
        self.assertEqual(prog.cid, 'simpos##boot_probe')
        one(prog, 'invoke')                              # printed invoke/1
        pco = m.lib.build('simpos##boot_probe')
        seen = {e.name: K.deref(v) for e, v in zip(pco.instance_slots, prog.slots)}
        p = seen['seen_p']
        # the program ran in the boot process, the sole boot_process
        self.assertEqual(p.cid, 'simpos##boot_process')
        self.assertIs(seen['seen_b'], p)
        self.assertIs(seen['seen_top'], prog)
        self.assertEqual(seen['seen_status'], K.Atom('active'))
        (b,) = one(boot, 'get_instance', K.Var())
        self.assertIs(b, p)
        # after invoke/1: the stack is empty and the printed resign/1 let
        # the process die (status nil, TM-100 p11)
        bco = m.lib.build('simpos##boot_process')
        st = {e.name: K.deref(v) for e, v in zip(bco.instance_slots, p.slots)}
        self.assertEqual(st['status'], K.Atom('nil'))
        self.assertEqual(len(one(st['invocation_stack'], 'empty')), 0)
        # boot_process's own :create and :activate: overridden, not printed
        for recv, sel, n in ((p, 'activate', 2), (boot, 'create', 2), (boot, 'create', 3)):
            m.reset()
            with self.assertRaises(K.Refusal) as cm:
                any(True for _ in m.solve_send(recv, sel, [K.Var() for _ in range(n - 1)] + [recv]))
            self.assertEqual(cm.exception.cause, 'simpos')
            self.assertIn('overrides', cm.exception.detail)
        # the next route step (B3) is blocked: a second process is made,
        # its parent the boot process, and activate/2 stops at status/3
        areas = K.Cons(K.Atom('free'), K.Cons(K.Atom('free'), K.Cons(K.Atom('free'), K.Cons(
            K.Atom('free'), K.Atom('[]')))))
        (p2, _a) = one(K.ClassRef('simpos##process'), 'create', K.Var(), areas)
        pco2 = m.lib.build('simpos##process')
        s2 = {e.name: K.deref(v) for e, v in zip(pco2.instance_slots, p2.slots)}
        self.assertEqual((p2.cid, s2['status']), ('simpos##process', K.Atom('dormant')))
        self.assertIs(s2['parent_process'], p)
        m.reset()
        with self.assertRaises(K.Refusal) as cm:
            any(True for _ in m.solve_send(p2, 'activate', [prog, p2]))
        self.assertIn('simpos##process:status/3', cm.exception.detail)
        # the held second call site of status/3: pimmcsp##pseudo_pe_process
        # release/1 @17a-17e, (dormant, on_release), before its
        # :get_instance(#boot_process, _) @17f-183
        m.reset()
        pe = K.make_instance(m, 'pimmcsp##pseudo_pe_process')
        m.stop_before = {('status', 3)}
        try:
            with self.assertRaises(K.CreatorStopped) as cm:
                any(True for _ in m.solve_send(pe, 'release', [pe]))
        finally:
            m.stop_before = None
        self.assertEqual(cm.exception.args[2][:2], [K.Atom('dormant'), K.Atom('on_release')])
        self.assertIs(cm.exception.args[2][2], pe)

    def test_step3h_tcpip_recipe(self):
        # step 3h: pimos_tcpip_socket's recipe (kl0 _tcpip_socket): a front
        # end pushed by the printed as_program assign/1, create_socket/9
        # run to activate/2, the front end popped by resign_core/1
        m = K.fep_machine()
        (s,) = K.call_class_method(m, 'simpos##process', 'self', [K.Var()])
        proc = s[0]
        pco = m.lib.build('simpos##process')
        stack = K.deref(proc.slots[m.lib.slot_number(pco, 'instance', 'invocation_stack')])
        self.send(stack, 'clear')
        dev = K.RECIPES[K.TCPIP](m)
        co = m.lib.build(dev.cid)
        sl = {e.name.split('$')[-1]: K.deref(v) for e, v in zip(co.instance_slots, dev.slots)}
        self.assertEqual((sl['fep_object'].cid, sl['fep_process'], sl['device_id'], sl['output_stream'].cid),
                         (K.FRONT_END, proc, K.REQUEST_ID, 'simpos##stream'))
        # the stack is left as it was found
        self.assertEqual(K.resolve(stack.slots[0]), K.NIL)
        # attention/1 puts {Id, 3} on the output stream, as the timer's does
        q = K.resolve(sl['output_stream'].slots[0].slots[0])
        self.assertEqual(q, K.NIL)
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(dev, 'attention', [dev])))
        q = K.resolve(sl['output_stream'].slots[0].slots[0])
        self.assertEqual(K.deref(q.args[0]).codes(), [16, 0, 3, 0])

    def test_step3h_children(self):
        # process:children/2 (step 3h, INTERPOLATED: TM-100 Fig. 3.1's slot
        # children_processes; kappa2 FMP.ESP:621-625).  It answers the
        # slot's list; held pimos_scsi_front_end exterminate_child/0
        # (@50e-51e) takes its contents and sends exterminate/1 to each
        m = self.m
        m.reset()
        (s,) = K.call_class_method(m, 'simpos##process', 'self', [K.Var()])
        proc = s[0]
        co = m.lib.build('simpos##process')
        kids = proc.slots[m.lib.slot_number(co, 'instance', 'children_processes')]
        L = K.Var()
        self.assertEqual([K.resolve(L) is K.deref(kids) for _ in m.solve_send(proc, 'children', [L, proc])], [True])
        cid = 'pimfep##pimos_scsi_front_end'

        def exit1():
            m.reset()
            fe = K.make_instance(m, cid)
            try:
                return 'success' if any(True for _ in m.solve_send(fe, 'exit', [fe])) else 'failure'
            except K.Refusal as e:
                return e.detail
        self.send(kids, 'clear')
        try:
            # no children: exit/1 succeeds (its fep_type is the template
            # constant 0, which create/6 overwrites, @50: no shutdown branch)
            self.assertEqual(exit1(), 'success')
            # one child: the loop sends it exterminate/1 (not stood in)
            self.assertEqual(len(self.send(kids, 'add_last', proc)), 1)
            self.assertIn('exterminate/1', exit1())
        finally:
            self.send(kids, 'clear')

    def test_step3h_scsi_mode(self):
        # step 3h: the six pimscsi failures of step 3g, traced.  cmt and scsi
        # check their arguments in scsi_communicator check_arguments/2
        # (@130-147): each element goes to check_argument/2 (@93-10d).  The
        # `initiator` clause (@b7-bd) needs Obj!lun = initiator, which
        # scsi_common_if create/3 writes (@22-25); the `target` clause
        # (@be-c4) needs an integer lun, which create/4 writes (@46-49).
        # The census's new/2 instance keeps lun = 0, a target, as held
        # scsi_handler initiate_device/7 leaves the scsi it makes with
        # :new (@3cb-3d3, no lun written).  So low_if/2, send_request/5
        # and receive_request/5, which list `initiator`, fail through
        # @13f-147 (status software, detail arguments): held behaviour.
        m = self.m

        def run(cid, sel, lun):
            m.reset()
            o = K.make_instance(m, cid)
            if lun is not None:
                self.assertEqual(len(self.send(o, 'set_lun', lun)), 1)
            name, n = sel.split('/')
            try:
                r = 'success' if any(True for _ in m.solve_send(o, name, [K.Var() for _ in range(int(n) - 1)] + [o])) \
                    else 'failure'
            except K.Refusal as e:
                r = e.cause
            co = m.lib.build(cid)
            s = {e.name.split('$')[-1]: K.deref(v) for e, v in zip(co.instance_slots, o.slots)}
            return r, s['status'], s['detail']
        sw = (K.Atom('software'), K.Atom('arguments'))
        for cid in ('pimscsi##cmt', 'pimscsi##scsi'):
            for sel in ('low_if/2', 'send_request/5', 'receive_request/5'):
                self.assertEqual(run(cid, sel, None), ('failure',) + sw, (cid, sel))
                # an initiator (lun := initiator by the held set_lun/2) gets
                # past `initiator`: low_if/2 to an opcode (blt e0, past the
                # blt e1 of include_item_1/3 since step 3h), the others to
                # the unit check on the census's unbound unit
                want = 'opcode' if sel == 'low_if/2' else 'unbound argument'
                self.assertEqual(run(cid, sel, K.Atom('initiator'))[0], want, (cid, sel))
            # a target method: on lun 0 it reaches the unbound unit; on an
            # initiator it fails at `target` (@c3, integer(lun))
            self.assertEqual(run(cid, 'send_data/4', None)[0], 'unbound argument')
            self.assertEqual(run(cid, 'send_data/4', K.Atom('initiator')), ('failure',) + sw)

    def test_step3f_window_protocol(self):
        # pmacs_window's geometry, title and display methods (step 3f,
        # INTERPOLATED from window.md §2.1-2.3): a setter's value is read
        # back by its getter; reshape/5 sets position and size
        m = self.m
        m.reset()
        (r,) = K.call_class_method(m, 'simpos##pmacs_window', 'create', [K.NIL, K.Var()])
        w = r[1]
        self.send(w, 'set_position', 3, 4)
        self.assertEqual(self.send(w, 'get_position', K.Var(), K.Var()), [[3, 4]])
        self.send(w, 'reshape', 5, 6, 70, 80)
        self.assertEqual(self.send(w, 'get_position', K.Var(), K.Var()), [[5, 6]])
        self.assertEqual(self.send(w, 'get_size', K.Var(), K.Var()), [[70, 80]])
        self.send(w, 'set_text_size', 80, 24)
        self.assertEqual(self.send(w, 'get_text_size', K.Var(), K.Var()), [[80, 24]])
        t = K.Str('log')
        self.send(w, 'set_title', t)
        (g,) = self.send(w, 'get_title', K.Var())
        self.assertIs(g[0], t)
        for sel in ('activate', 'deactivate', 'show', 'hide', 'beep', 'flash'):
            self.assertEqual(self.send(w, sel), [[]], sel)

    def test_step3f_library_and_symbolizer(self):
        # SIMPOS's library and the symbolizer's atom table (kl0
        # SIMPOS_MODELS, INTERPOLATED, OURS)
        m = K.fep_machine()

        def call(cid, name, args):
            # the models are not templates: send directly (call_class_method
            # builds the class first)
            m.reset()
            regs = list(args) + [K.ClassRef(cid)]
            return [[K.resolve(a) for a in args] for _ in m.solve_send(K.ClassRef(cid), name, regs)]
        m.reset()
        self.assertEqual(len(call('simpos##library', 'assign', [])), 1)
        a = K.Atom('pimfep##pimos_timer')
        for kind, n in (('object', 1), ('template_file', 0)):
            m.reset()
            self.assertEqual(len(call('simpos##library', 'check_info', [a, K.Atom(kind)])), n)
        m.reset()
        self.assertEqual(len(call('simpos##library', 'check_info',
                                                 [K.Atom('no_such_class'), K.Atom('object')])), 0)
        m.reset()
        (r,) = call('simpos##library', 'get_class_object', [a, K.Var()])
        self.assertEqual(r[1].cid, 'pimfep##pimos_timer')
        # a bare name two loaded packages define, with no sending class
        # (a direct call): refused
        with self.assertRaises(K.Refusal):
            call('simpos##library', 'get_class_object',
                                [K.Atom('pimos_remote_login_replier'), K.Var()])
        m.reset()
        (r,) = call('simpos##symbolizer', 'enter_atom', [K.Var(), K.Str('abc')])
        self.assertIs(r[0], K.Atom('abc'))
        m.reset()
        with self.assertRaises(K.Refusal):
            call('simpos##symbolizer', 'enter_atom', [K.Var(), K.Var()])
        # create_string_io/10 makes the named program in pimfep (the
        # sender's package; pimmcsp has a class of the same name)
        dev = K.RECIPES['pimfep##pimos_remote_login_replier'](m)
        self.assertEqual(dev.cid, 'pimfep##pimos_remote_login_replier')
        co = m.lib.build(dev.cid)
        s = {e.name.split('$')[-1]: K.deref(v) for e, v in zip(co.instance_slots, dev.slots)}
        self.assertEqual([getattr(s[n], 'cid', s[n]) for n in
                          ('input_stream', 'output_stream', 'creation_status_stream')],
                         ['simpos##stream'] * 3)


if __name__ == '__main__':
    unittest.main()
