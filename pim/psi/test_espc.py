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
import simpos_fs as FS  # noqa: E402

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
:quo(C,X,Y,Z) :- Z = X/Y;
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
        # X+Y compiles since step 3c (blt 40, 2026-11-24), X*Y since
        # 2026-11-25 (blt 42); X/Y is still refused
        self.assertEqual(got, {'quo': 'arithmetic X/Y', 'ne': 'comparison =\\=',
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

    def test_multiply(self):
        # Z = X*Y on two registers is blt 42 multiply with the result over
        # the first operand (kl0_opcodes.tsv row 42: paragraph##h layout/2
        # @73 `42 01 02 01`, h.esp:21), emitted since 2026-11-25.
        # Injection (observed 2026-11-25, espc.py from a copy, restored by
        # copy, cmp clean; full test_espc and test_kl0 runs): `*` emitted
        # as blt 40 add: this test FAILS (the opcode) and MacroBank
        # test_kappa2 FAILS (1,513 exact, not 1,514: the held cells of
        # with_kappaMDU_table_with_pp tab/3 have blt 42), nothing else;
        # test_kl0 OK
        t = compile_one(self.T)
        self.assertIn(0x42, [c[1] for c in code(t, 'mul') if c[0] == 0x21])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##t', 'mul', [3, 4, K.Var()])
        self.assertEqual(K.resolve(r[2]), 12)


class RegisterCache(unittest.TestCase):
    """espc's register cache after a register is overwritten (2026-11-25).
    A free register may still be recorded as holding a cached copy of a
    permanent variable; a write into it that did not replace the record
    left the cache naming the register, and a later read of the variable
    took the new contents.  Two writers did that: slotset's put of the
    slot name (found by window M5: window_pane create/7, `add on w`), and
    a built-in's output register when the output is a constant (the
    register is read, not bound, so the stale record was restored).  The
    fix drops the record in Regs.lowest(), where every such register is
    handed out.

    In each clause below Z (A2) and the receiver O (A3) are permanent:
    they live across ok/1.  ok3/3 is the next call, so A0-A2 are its
    pending arguments and an arithmetic result goes to A3 or above.

    Injections (2026-11-25, observed; each from a copy of espc.py,
    restored by copy, cmp clean):
    - the whole fix reverted (full test_espc.py and test_kl0.py runs):
      test_slot_name_put ([3, 106, b]: `O!c := Z` stored the atom b, the
      slot name of `O!b := X + 6`, put in the register that cached Z) and
      test_builtin_output_to_constant ([0, 0, 5]: the element read into
      W's register, where W is 3) FAIL, nothing else; test_kl0 OK.  (On
      the same compiler `O!c := Z + 1` refused `add on b`, by a scratch
      run; the test stops at name1.)
    - only the eviction in Regs.lowest() removed, slotset's own record of
      the name kept (full test_espc.py run): only
      test_builtin_output_to_constant FAILS.
      Slotset's record is then redundant with the eviction (removing it
      alone fails nothing); it is kept so that the name's register is
      recorded where it is written."""
    T = '''class rc has
instance
attribute a := 0, b := 0, c := 0;
:name1(O, X, Y, Z) :- ok(O), O!a := Z, O!b := X + 6, O!c := Z, ok3(O, X, Y);
:name2(O, X, Y, Z) :- ok(O), O!a := Z, O!b := X + 6, O!c := Z + 1, ok3(O, X, Y);
:elem(O, X, Y, Z) :- ok(O), W = Z, vector_element(Y, 0, 5), O!c := W, ok3(O, W, Y), ok(W);
:get(O, A, B, C) :- A = O!a, B = O!b, C = O!c;
local
ok(_);
ok3(_, _, _);
end.'''

    @classmethod
    def setUpClass(cls):
        cls.t = compile_one(cls.T)
        assert not cls.t.refusals, cls.t.refusals

    def run_set(self, sel):
        m = K.Machine(espc.library([self.t]))
        cid = K.ClassRef('user##rc')
        (o,) = [K.resolve(m.x[0]) for _ in m.solve_send(cid, 'new', [K.Var(), cid])]
        m.reset()
        n = sum(1 for _ in m.solve_send(o, sel, [100, K.Vec([5, 6]), 3, o]))
        self.assertEqual(n, 1)
        m.reset()
        regs = [K.Var(), K.Var(), K.Var(), o]
        (got,) = [[K.resolve(r) for r in regs[:3]] for _ in m.solve_send(o, 'get', regs)]
        return got

    def test_slot_name_put(self):
        self.assertEqual(self.run_set('name1'), [3, 106, 3])
        self.assertEqual(self.run_set('name2'), [3, 106, 4])

    def test_builtin_output_to_constant(self):
        self.assertEqual(self.run_set('elem'), [0, 0, 3])

    def test_compare_reads_its_own_operand(self):
        # `X < X + 1`: the comparison marked X's register 'cmp' while Y
        # was put, so Y's read of X lost it: a KeyError for a temporary, a
        # TypeError at the allocate for a head argument not yet saved
        # (both observed on the compiler before 2026-11-25).  X's register
        # now keeps its record, as in arith().  Injection (observed, from
        # a copy, restored by copy, cmp clean; full test_espc.py): that
        # keeping reverted, only this test ERRORS
        t = compile_one('''class cmpx has
:temp(C, X) :- X < X + 1;
:temp2(C, X, Y) :- X + 1 > X, Y = X;
:head(C, X) :- X < X + 1, ok(X), ok(X);
local
ok(_);
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        for sel in ('temp', 'head'):
            self.assertEqual(len(K.call_class_method(m, 'user##cmpx', sel, [5])), 1)
        (r,) = K.call_class_method(m, 'user##cmpx', 'temp2', [5, K.Var()])
        self.assertEqual(K.resolve(r[1]), 5)


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
        # `{}` and four-element vectors): none lost.  1241 / 258 before
        # X*Y on two registers (blt 42, 2026-11-25): 39 refused predicates
        # compile, none exact, no compared one changes its class
        self.assertEqual((c['pred compared'], c['pred exact']), (1280, 258))
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
        # reset_all_at/2 now run the held code too, and agree.  Step 3n
        # (pmi 36 rowed): graph_status_element create/3, get/2 and set/2
        # run the held code too and agree: 'refused held only' 3 -> 0
        self.assertEqual(dict(self.r['census']), {'same outcome': 101, 'both refused': 86,
                                                  'refused compiled only': 40})


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
        # with X*Y on two registers (blt 42, 2026-11-25): 12,871 compared,
        # 1,514 exact (with_kappaMDU_table_with_pp tab/3 newly exact; no
        # compared predicate changes its class)
        self.assertEqual((c['pred compared'], c['pred exact']), (12871, 1514))
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
            'simpos##abort_handler', 'simpos##alarm_watch', 'simpos##as_boot_program', 'simpos##as_class_with_lock',
            'simpos##as_message', 'simpos##as_program', 'simpos##as_resource',
            'simpos##binary_file', 'simpos##boot_process',
            'simpos##bounded_channel', 'simpos##bounded_post_queue', 'simpos##buffer_region', 'simpos##channel',
            'simpos##common_network', 'simpos##context', 'simpos##coordinator',
            'simpos##coordinator_program', 'simpos##date_time', 'simpos##directory',
            'simpos##e_string', 'simpos##editor_command_interpreter', 'simpos##editor_text_buffer',
            'simpos##font', 'simpos##hash_index', 'simpos##list', 'simpos##list_index',
            'simpos##menu_pane',
            'simpos##message', 'simpos##monogyny_list_index', 'simpos##name', 'simpos##network_listener_buffer',
            'simpos##network_node_name', 'simpos##network_subsystem',
            'simpos##password_list', 'simpos##pathname', 'simpos##pmacs_request', 'simpos##pmacs_window',
            'simpos##port', 'simpos##post_queue',
            'simpos##post_queue_for_message', 'simpos##process', 'simpos##process_clock',
            'simpos##semaphore', 'simpos##standard_editor',
            'simpos##standard_input_file', 'simpos##standard_io_window', 'simpos##status_band',
            'simpos##stream', 'simpos##string', 'simpos##symbolizer',
            'simpos##tcpip_network_subsystem', 'simpos##time',
            'simpos##trace', 'simpos##user', 'simpos##waiting_frame', 'simpos##waiting_queue',
            'simpos##window_pane', 'simpos##with_link', 'simpos##with_lock', 'simpos##world'])
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
        # §2.4, putl/2) was not.  Window M4 stood in putl/2; its input,
        # getl/2, is not
        self.assertIn('simpos##pmacs_window:getl/2', detail)
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
        # the stand-in is part of the lost class (kl0, step 3e).  The
        # witness was pimos_window_editor carriage_return/1 until window
        # M4 gave standard_editor a carriage_return/1 primary (INFERENCE,
        # standard_editor.esp); simpos_user_device exit/1 is another
        cause, detail = self.refusal(m, 'pimfep##simpos_user_device', 'instance', 'exit/1')
        self.assertEqual(cause, 'simpos')
        self.assertIn('no primary in the held classes; stand-in ancestors simpos##as_program', detail)

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
        # step 3i: pmi 3b and 6c witnessed (LOADER.ESP:118-126,
        # RDMSOPE.ESP:285-291): 757 / 219 / 427 -> 759 / 219 / 425.  The
        # five pseudo_scsi rows that stopped at 6c @13d run into local
        # command/2 (a c6 entry): command/2 and command_with_hook/2 succeed
        # (the census's unbound first argument takes clause 1,
        # `command([], _)`; unbound probing, not progress); send_data/4,
        # receive_data/4 and receive_command/3 stop at the unprinted
        # as_resource assigned/1
        # step 3i: blt 00 and e0 witnessed (g_window.esp:148, bar2_h.esp:135,
        # as_pred.esp:419-422): 759 / 219 / 425 -> 759 / 221 / 423.  cmt
        # and scsi transfer/6 go from blt e0 (scsi_communicator
        # include_item_1/3 @26b) to failure: the census's unbound item is
        # neither an integer nor an atom (unbound probing, not progress)
        # step 3i: pmi c8 witnessed (HLCSESITTK.ESP:408-424): 759 / 221 / 423
        # -> 763 / 221 / 419.  The four expand/7 (scsi_fep_macro,
        # scsi_macro, pseudo_scsi_macro, scsi_macro_core) succeed: the
        # census's unbound first argument takes c8's try chain and the
        # first clause's get_constant binds it (unbound probing, not
        # progress)
        # step 3i: blt 1a new_stack_vector (mcd.esp:112-116, KP_BFMOM.ESP:
        # 181-185): 763 / 221 / 419 -> 768 / 221 / 414.  melt_arguments/2
        # (cmt, scsi, scsi_communicator) and melt_method/3 (cmt, scsi)
        # succeed: valid_size is its template slot constant 0, so the
        # melted vector is {} (a census artifact, not progress);
        # scsi_communicator melt_method/3 stops at get_content/2, not in
        # the class
        # step 3i: pmi c9's first target is [] only (cts_post.esp:18-21):
        # 768 / 221 / 414 -> 767 / 221 / 415.  scsi shutdown/1 no longer
        # succeeds: scsi_low_if local check_status/3 @115 sent the atom
        # handler_dead to its nil target (@121 `d2`, past the get_nil @120);
        # it now takes the other target @125 and raises (scsi_error
        # raise/5, not held).  The success was the c9 fault, not progress
        # step 3j (psi/README.md "Step 3j"): 1,420 -> 1,466 rows: 46
        # inherited stand-in methods are new rows (as_program
        # entry_of_invoke/2 in 28 classes, all success; as_resource
        # assign/1, assigned/1 and resign/1 in 6, 6 success and 12
        # failure), none held.  Of the 1,420 held rows, 16 change: the 11
        # device creators' activate/2 pass status/3, entry_of_invoke/2 and
        # the context and stop at the ready queue, which the census's boot
        # process has not made (`add/2 to 0`, a slot constant), and the 5
        # pseudo_scsi rows pass assigned/1 (it fails: nothing assigned)
        # and stop at class_object of 1900544 on the not_assigned path.
        # Not progress: the held rows' outcomes are unchanged (767 / 221 /
        # 415 over the 1,420)
        # step 3l: simpos_user create/4 now fails at identify/4 (no user is
        # registered in a census row: the registry is a class slot, which
        # the census drops), where it was refused: not progress.  801 /
        # 234 / 414.  Step 3l, the window stand-ins: pimos_fep_superviser
        # log_size_input_window/2 makes its window (OURS) and succeeds; the
        # login requester's three rows move to get_number/2 on its
        # process's context, unset in a census row.  802 / 234 / 413
        # step 3m (row by row against 167ea83d): 1,466 -> 1,468 rows, the
        # message stand-in's create/2 inherited by pimscsi cmt and scsi
        # (nature simpos##message), both success: artifacts, not held.
        # Two held rows change outcome, refused -> success, both past
        # class_object/2 (kl0 dispatch, INTERPOLATED): replier io/4 and
        # scsi_handler exit/1.  Six rows move their stop.  806 / 234 / 411
        # step 3n (row by row against 2eda555c): 15 rows change.  Real:
        # pimos_scsi_front_end create/6 refused -> success (abort_handler,
        # set_area_limit_execution/7, set_package/2, grant_stream/2 stood
        # in, the path of the bridged run).  blt 0d object/3 rowed
        # (INFERENCE): its 10 rows go on, 3 to success (remote_stream
        # set_keepalive_option/1, scsi_handler class_deletion_hook/1,
        # scsi_load_test close/1) and 1 to failure (set_receive_timer/2);
        # traced, object/3 meets only a slot's initial value in these rows
        # (the atoms none and nil, or a census slot constant) and fails
        # on it: census artifacts, not progress; the other 6 go on to the
        # next stop.
        # monogyny_list_index stood in: simpos_user identify/4, regist/4
        # and setup_process/4 refused -> failure (identify/4: no user in a
        # census row's empty index; regist/4 and so setup_process/4 fail
        # too, the cause not traced).  exterminate_fep/1 moves to the
        # census's missing ready queue (exterminate/1 stood in).
        # 810 / 238 / 403
        # window M4/M6 (row by row against the branch's base 9031ff05,
        # 2026-11-25): 1,468 -> 1,483 rows, all 15 new rows inherited
        # from stand-ins, no row removed, no held row changes outcome:
        # with_lock's lock_with_hook/1 and unlock_with_hook/1 in the
        # three device tables (6, success); pmacs_window's new methods in
        # pimos_window: get_interpreter/2, has_been_reshaped/1,
        # selected/1, deselect_window/1, status_name/3 success,
        # contains/3 failure (no pane), input_data/2, typed/2, putl/2
        # refused (a census instance has no interpreter: slot constant).
        # pimos_window activate/1, show/1, flash/1 stay success (a window
        # not made by create/3 is not drawn, pmacs_window.esp open/1).
        # The editor's set_font/4 moves its stop from opcode blt 69 to
        # not_equal_string on the census's unbound font name.
        # 821 / 239 / 406
        self.assertEqual((len(rows), out), (1483, {'success': 821, 'failure': 239, 'refused': 406, 'exception': 16,
                                                   'step limit': 1}))
        eoi = [r[3] for r in rows if r[2] == 'entry_of_invoke/2']
        self.assertEqual((len(eoi), set(eoi)), (28, {'success'}))
        # assigned/1 is as_resource's alone (assign/1 is as_program's too)
        self.assertEqual(sorted(r[3] for r in rows if r[2] == 'assigned/1'), ['failure'] * 6)
        # slot constants 154 -> 157 in step 3l: the login requester's three
        # rows (get_number/2 to its process's unset context); 157 -> 154 in
        # window M0: font create/3 now reads its file, and the census mounts
        # no file system, so those three rows stop earlier, at directory
        # retrieve/3 (a stop of the census machine, not of the route);
        # 154 -> 158 in window M4: pimos_window input_data/2, typed/2,
        # putl/2 (new rows) and the editor's carriage_return/1 (was
        # 'simpos', now get_interpreter/2 to the census window's unset
        # editor slot) stop at the census's slot constants
        self.assertEqual(sum(1 for r in rows if r[4] == 'receiver a slot constant'), 158)
        self.assertEqual(sorted(r[2] for r in rows if r[0] == 'pimfep##pimos_login_requester'
                                and 'no file system is mounted' in r[5]),
                         ['goal/1', 'initiate/1', 'invoke/1'])
        self.assertNotIn('simpos##process:status/3', {K.simpos_target(r[5]) for r in rows})
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
        # step 3i: pmi 3b and 6c: the same five pseudo_scsi rows, 784 / 220
        # / 399 (two successes on an unbound argument, not progress); blt 00
        # and e0: the same two transfer/6 rows fail, 784 / 222 / 397; pmi
        # c8: the same four expand/7 succeed, 788 / 222 / 393; blt 1a: the
        # same six melt rows, 793 / 222 / 388; c9 [] only: scsi shutdown/1
        # raises, 792 / 222 / 389
        # step 3j: as in the plain census, 46 stand-in rows added (34
        # success, 12 failure) and 16 held rows changed (11 creators to
        # the missing ready queue, 5 pseudo_scsi past assigned/1): 826 /
        # 234 / 389, slot constants 94 -> 105
        # step 3k (row by row against master b62208d4, each checked alone
        # on a fresh machine): 4 rows change.  pimos_timer get_count/3 and
        # get_date_time/3 succeed (time:now/2, get_count/2 and date_time
        # INTERPOLATED, the reply's integer length word -1 from put_integer
        # sign-extended and stored in the 32-bit string: INFERENCE); the
        # editor's get_position/3 and get_inside_size/3 pass put_integer
        # `ffff` and stop at put/2 on the window's unset output stream (a
        # slot constant, the step 3g artifact).  828 / 234 / 387, slot
        # constants 105 -> 107.  Step 3l: simpos_user create/4 fails at
        # identify/4 (no registry in a census row): 828 / 235 / 386; the
        # window stand-ins, as in test_fep_census: 829 / 235 / 385.  Step
        # 3m: the two artifact rows of test_fep_census (success) and
        # scsi_handler exit/1 refused -> success (class_object/2); the
        # replier's io/4 moves to substring/7 16 -> 32 bits and to
        # set_string_element on an unbound argument.  832 / 235 / 384
        # step 3n (row by row against 2eda555c): 17 rows change: the 15
        # of test_fep_census, the same way, and substring/7 16 <-> 32 bits
        # (INFERENCE): the replier's io/5 refused -> success (a real move:
        # assemble/3 is the path of the bridged run), and the editor's
        # get_title/3 moves to put/2 on the window's unset output stream
        # (a slot constant, the step 3g artifact).  837 / 239 / 375
        # window M4/M6 (row by row against 9031ff05): the 15 new rows of
        # test_fep_census, here with recipes 13 success, contains/3 and
        # putl/2 failure; and two held rows refused -> success, both on
        # the console's path: pimos_window_editor getl/3 (getl_from_buffer
        # on the editor_text_buffer stand-in) and carriage_return/1
        # (standard_editor's primary, INFERENCE).  852 / 241 / 373
        self.assertEqual((len(rows), out), (1483, {'success': 852, 'failure': 241, 'refused': 373,
                                                   'exception': 16, 'step limit': 1}))
        slot_const = sum(1 for r in rows if r[4] == 'receiver a slot constant')
        # step 3l: 107 -> 110, as in test_fep_census; step 3n: 111, get_title/3;
        # window M0: 111 -> 108 (the login requester's three rows, as in
        # test_fep_census); window M4: 108 -> 114, the editor's
        # buffer_name/3, clear/3, reshape/7, reshape_by_mouse/3,
        # set_inside_size/5, set_size/3 go from 'simpos' (an unstood
        # pmacs_window or editor method) to put/2 on the window's unset
        # output stream (the step 3g artifact, as get_title/3)
        self.assertEqual(slot_const, 114)
        self.assertEqual(by[('pimos_timer', 'instance', 'get_count/3')][0], 'success')
        self.assertEqual(by[('pimos_timer', 'instance', 'get_date_time/3')][0], 'success')
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
        # 17, and since step 3h pimos_tcpip_socket loop_main/1: 18; step
        # 3n: 19, the front end's exterminate_fep/1 (exterminate/1 stood
        # in, then the census's missing ready queue); window M4: 21,
        # pimos_window_process goal/1 and invoke/1 (were 'simpos' at
        # get_interpreter/2), now waiting in the command interpreter's
        # get on its input stream, the console's own wait
        self.assertEqual(sum(1 for r in rows if r[4] == 'would suspend'), 21)
        self.assertNotIn('simpos##stream:see/2', {K.simpos_target(r[5]) for r in rows})
        self.assertEqual(by[('as_pimos_device', 'instance', 'loop_main/1')][:2],
                         ('refused', 'receiver a slot constant'))
        # pimos_file: with the open mode `read` (step 3g), initiate/1 and
        # goal/1 reach the SIMPOS directory (step 3f's failure and
        # success were on a stream in the open-mode argument)
        # step 3l: the directory's retrieve/3 is modelled (INTERPOLATED,
        # kl0 directory_retrieve); the recipe gives no pathname, so it
        # refuses on the unbound one
        for sel in ('initiate/1', 'goal/1'):
            self.assertEqual(by[('pimos_file', 'instance', sel)][:2], ('refused', 'unbound argument'))
            self.assertIn('directory retrieve/3 on an unbound pathname',
                          by[('pimos_file', 'instance', sel)][2])
        # step 3g: the device replies to the request REQUEST_ID
        for c in ('pimos_timer', 'pimos_directory', 'pimos_window_process', 'pimos_file',
                  'simpos_user_device', 'pimos_remote_login_replier', 'pimos_standard_io_window',
                  'pimos_remote_login_server'):
            self.assertEqual(by[(c, 'instance', 'attention/1')][0], 'success', c)
        self.assertEqual(by[('pimos_timer', 'instance', 'close/3')][0], 'success')
        self.assertEqual(by[('pimos_timer', 'instance', 'abort_timer/3')][0], 'success')
        # the editor reaches pimos_window's lost pmacs_window protocol
        # (get_interpreter/2 was not stood in; window M4 stood it in, and
        # clear/3 goes on to its reply, put/2 on the census window's unset
        # output stream, as get_title/3 below)
        self.assertEqual(by[('pimos_window_editor', 'instance', 'clear/3')],
                         ('refused', 'receiver a slot constant', 'send put/2 to 0 (a slot constant)'))
        # with the interpolated geometry and title (step 3f), get_title/3
        # runs through the window to its reply; with the request (step 3g)
        # and blt 48 R != A, the reply's assembly stops at blt 36;
        # set_size/3 at the has_been_reshaped/1 callback.  Step 3m: blt 36
        # rowed (substring/7); the assembler asks it for a 16-bit string
        # read as 32-bit elements (fep_message_assembler @122), unwitnessed.
        # Step 3n: 16 to 32 bits inferred; the reply is assembled and put on
        # the window's output stream, unset in a census row (a slot
        # constant, the step 3g artifact)
        self.assertEqual(by[('pimos_window_editor', 'instance', 'get_title/3')],
                         ('refused', 'receiver a slot constant', 'send put/2 to 0 (a slot constant)'))
        # set_size/3: past has_been_reshaped/1 since window M4, to its reply
        self.assertEqual(by[('pimos_window_editor', 'instance', 'set_size/3')],
                         ('refused', 'receiver a slot constant', 'send put/2 to 0 (a slot constant)'))
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
        # and goes on to its local refute/3.  Until step 3k it stopped at
        # fep_message_assembler disassemble/3's unwitnessed blt 6f; since
        # step 3k (blt 6f list_to_vector) the close request (60) runs to
        # its end: the device replies {16, 1}, sets its close flag and
        # loop_main/1 ends
        dev = K.RECIPES['pimfep##pimos_timer'](m)
        co = m.lib.build(dev.cid)
        sl = {e.name.split('$')[-1]: K.deref(v) for e, v in zip(co.instance_slots, dev.slots)}
        inp, out = sl['input_stream'], sl['output_stream']
        msg = K.Str('', 32)
        msg.set_codes([16, 0, 60, 0])
        m.reset()
        self.assertEqual(len(list(m.solve_send(inp, 'put', [msg, inp]))), 1)
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(dev, 'loop_main', [dev])))
        self.assertEqual(repr(K.resolve(inp.slots[0].slots[0])), '[]')
        sl = {e.name.split('$')[-1]: K.deref(v) for e, v in zip(co.instance_slots, dev.slots)}
        self.assertEqual(sl['close_flag'], K.Atom('closed'))
        m.reset()
        (reply,) = [K.deref(x) for x in [K.Var()] if any(True for _ in m.solve_send(out, 'get', [x, out]))]
        self.assertEqual(reply.codes(), [16, 0, 1, 0])

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
            # step 3j: 46 stand-in rows; 3m: 2 (message create/2); window
            # M4/M6: 15 (test_fep_census)
            self.assertEqual(len(fwd), 1483)
            diff = sorted(k for k in fwd if fwd[k] != bwd.get(k))
            self.assertEqual(diff, [], recipes is not None)
        # the order effect step 3h left open: set_log_table/2's unbound
        # argument no longer reaches dump_log/1, which goes on to the
        # message window (pmacs_window putl/2, not stood in; window M4
        # stood it in, and the row goes on to getl/2, not stood in)
        by = norm(K.census_fep(K.fep_machine()))
        self.assertEqual(by[('pimfep##pimfep_message_log', 'class', 'dump_log/1')][:2],
                         ('refused', 'simpos'))
        self.assertIn('pmacs_window:getl/2', by[('pimfep##pimfep_message_log', 'class', 'dump_log/1')][2])

    def test_step3i_boot(self):
        # step 3i, docs/simpos/boot_route.md B2: the boot process (TM-100
        # p6, p13; TR-056 p21; held pimmcsp##pseudo_pe_process release/1)
        # runs a boot program (as_boot_program, TM-100 p13) with the
        # printed as_program invoke/1.  boot_probe is an OURS test class.
        # Injections, observed at step 3i, before the step 3j tests existed
        # (2026-11-25; inject from a backup, restore by copy, cmp clean;
        # test_kl0.py stayed OK in all three; I1 and I3 not re-run since):
        #   I1 process.esp self/2 back to :new(Class, P): this test ERROR,
        #      test_printed_process_slots FAIL, nothing else.
        #   I2 the three boot_process_override SIMPOS_MODELS rows deleted:
        #      this test FAIL, nothing else.  Step 3j (two rows are now
        #      stand-ins; observed with the step 3j tests present): J9, the
        #      create/3 row deleted, this test FAIL, nothing else
        #      (test_kl0.py OK).
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
        # boot_process's own :create/3 is refused (step 3j stood in create/2
        # and activate/2: test_step3j_supervisor)
        m.reset()
        with self.assertRaises(K.Refusal) as cm:
            any(True for _ in m.solve_send(boot, 'create', [K.Var(), K.Var(), boot]))
        self.assertEqual(cm.exception.cause, 'simpos')
        self.assertIn('overrides', cm.exception.detail)
        # a second process is made, its parent the boot process.  Step 3j:
        # its activate/2 passes status/3, entry_of_invoke/2 and the context,
        # and stops at the ready queue, which the boot process has not made
        # (it has not come under the supervisor: B3, test_step3j_supervisor)
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
        self.assertEqual((cm.exception.cause, cm.exception.detail),
                         ('receiver a slot constant', 'send add/2 to 0 (a slot constant)'))
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

    B3_PROBES = '''class b3_boot has
nature as_boot_program;
instance
attribute got, child, child_program, status_after, wait;
:goal(Prog) :-
    :create(#boot_process, B),
    :activate(B, Prog),
    :create(#stream, S),
    :create(#b3_child, C, S),
    :create(#process, P, [free,free,free,free]),
    :activate(P, C),
    :get(S, X),
    Prog!got := X, Prog!child := P, Prog!child_program := C,
    Prog!status_after := B!status,
    wait(Prog!wait);
local
wait(0) :- !;
wait(_) :- :create(#stream, S), :get(S, _);
end.
class b3_child has
nature as_program;
:create(Class, Obj, S) :- :create(Class, Obj), Obj!stream := S;
instance
attribute stream, seen_p, seen_top, seen_parent;
:goal(Obj) :- :self(#process, P), :invocation_stack(P, L), :get_first(L, Top),
    Obj!seen_p := P, Obj!seen_top := Top, Obj!seen_parent := P!parent_process,
    :put(Obj!stream, created);
end.'''

    B3N_EXTERMINATE = '''class b3n_x_boot has
nature as_boot_program;
instance
attribute got, child, child_program, after_seen := none, child_status;
:goal(Prog) :-
    :create(#boot_process, B),
    :activate(B, Prog),
    :create(#stream, S),
    :create(#b3n_x_child, C, S),
    :create(#process, P, [free,free,free,free]),
    :activate(P, C),
    :get(S, X),
    Prog!got := X, Prog!child := P, Prog!child_program := C,
    Prog!after_seen := C!after, Prog!child_status := P!status;
end.
class b3n_x_child has
nature as_program;
:create(Class, Obj, S) :- :create(Class, Obj), Obj!stream := S;
instance
attribute stream, after := 0;
:goal(Obj) :- :put(Obj!stream, created),
    :self(#process, P), :exterminate(P),
    Obj!after := yes;
end.'''

    def test_step3n_exterminate(self):
        # step 3n: a process that exterminates itself (as the held
        # pimos_scsi_front_end exit_program/1 @4da-4e2 does: `:self(#process,
        # P), :exterminate(P)`) is dead (status nil, standin/process.esp,
        # INTERPOLATED) and gives up the processor at once (kl0's
        # dispatcher, OURS): the goal after the exterminate never runs, and
        # the boot process, made ready by the child's put, runs on.  The
        # probes are OURS, in the shape of B3_PROBES.
        # Injection, observed (2026-11-25; kl0.py from a backup, restored
        # by copy, cmp clean): F10, kl0 'ifdead' does not give the
        # processor away: this test FAIL, and test_fep_census,
        # test_step3f_census_recipes and test_step3h_children FAIL (their
        # exterminate rows move); psi/test_fep_bridge.py stays OK.
        ts, failed = espc.compile_text(self.B3N_EXTERMINATE, 'simpos')
        self.assertFalse(failed)
        lib = K.load_six()
        for t in list(self.ts) + ts:
            lib.add(t)
        m = K.Machine(lib)
        sl = lambda o: {e.name: K.deref(v) for e, v in zip(m.lib.build(o.cid).instance_slots, o.slots)}
        m.reset()
        sols = []
        v = K.Var()
        for _ in m.solve_send(K.ClassRef('simpos##b3n_x_boot'), 'create', [v, K.ClassRef('simpos##b3n_x_boot')]):
            sols.append(K.deref(v))
            break
        (prog,) = sols
        m.reset()
        self.assertEqual(sum(1 for _ in m.solve_send(prog, 'invoke', [prog])), 1)
        s = sl(prog)
        self.assertEqual(s['got'], K.Atom('created'))
        self.assertEqual(s['after_seen'], 0)
        self.assertEqual(s['child_status'], K.Atom('nil'))

    def test_step3n_monogyny_list_index(self):
        # step 3n: monogyny_list_index (INFERENCE: a list_index holding one
        # object per key; pimfep##simpos_user regist/4 @4d-61 put_at/3,
        # identify/4 @66-72 get_at/3).  A second put_at/3 under a key
        # replaces the first; get_at/3 fails on a key never put.
        # Injection, observed (2026-11-25; standin/monogyny_list_index.esp
        # from a backup, restored by copy, cmp clean): M1, put_at/3 without
        # the removal: this test FAIL, nothing else in this file.
        m = self.m
        m.reset()
        ((i,),) = K.call_class_method(m, 'simpos##monogyny_list_index', 'create', [K.Var()])
        a, b = K.Str('pmpsi'), K.Str('pmpsi')
        self.assertEqual(len(self.send(i, 'put_at', K.Atom('first'), a)), 1)
        self.assertEqual(len(self.send(i, 'put_at', K.Atom('second'), b)), 1)
        self.assertEqual(repr(self.send(i, 'get_contents_with_key', K.Var())),
                         "[[[{second,string#'pmpsi'}]]]")
        self.assertEqual(repr(self.send(i, 'get_at', K.Var(), K.Str('pmpsi'))), "[[second, string#'pmpsi']]")
        self.assertEqual(self.send(i, 'get_at', K.Var(), K.Str('other')), [])

    def test_step3j_supervisor(self):
        # step 3j, docs/simpos/boot_route.md B3: the boot process comes under
        # the supervisor (its own :create and :activate, INTERPOLATED,
        # TR-056 p21) and a second process runs.  The probes are OURS, in
        # the shape of held kappa2 kernel/itr/ITRSES.ESP:111-116 and
        # utility/mop/MOPMANAGER.ESP:165-172 (CORRECTED step 3k: first
        # cited :162-168) with MOPKAPPA.ESP goal/1 (:31-37): the
        # parent makes a stream, a program holding it and a process
        # (create/3, [free,free,free,free]), activates the process with the
        # program and does :get on the stream; the child's goal :puts.
        # Everything they send is printed (process activate/2, suspend/2,
        # resume/2, stream put/2 and get/2, as_program invoke/1) or a
        # labelled stand-in (status/3, clear_masks/1, entry_of_invoke/2,
        # context, boot_process create/2 and activate/2), and the switch is
        # kl0's dispatcher (OURS).
        # Injections, observed (2026-11-25; from a backup, restored by copy,
        # cmp clean; test_kl0.py stayed OK in all):
        #   J1 status/3 does not set: this test FAIL, nothing else.
        #   J2 status/3 succeeds on a mismatch: this test FAIL, nothing else.
        #   J3 kl0 'yield' does not switch: this test and
        #      test_step3j_fep_device ERROR, nothing else.
        #   J4 entry {Program, goal}: the same two ERROR, nothing else.
        #   J5 boot activate/2 does not join the ready queue: the same two
        #      ERROR, nothing else.
        #   J7 the dispatcher does not set `current`: the same two ERROR.
        #   J8 no 63-context limit: this test FAIL, nothing else.
        #   J10 kl0 'exit' halts instead of dispatching: this test ERROR,
        #      nothing else.
        #   J13 clear_masks/1 a no-op (the direct check below): this test
        #      FAIL, nothing else.
        #   J14 context activate/1 a no-op: this test and
        #      test_step3j_fep_device ERROR, nothing else.
        #   J15 create/3 does not store the context: those two ERROR and
        #      test_step3i_boot FAIL, nothing else.
        ts, failed = espc.compile_text(self.B3_PROBES, 'simpos')
        self.assertFalse(failed)
        lib = K.load_six()
        for t in list(self.ts) + ts:
            lib.add(t)
        m = K.Machine(lib)
        sl = lambda o: {e.name: K.deref(v) for e, v in zip(m.lib.build(o.cid).instance_slots, o.slots)}

        def one(recv, sel, *args):
            m.reset()
            sols = [[K.deref(a) for a in args] for _ in m.solve_send(recv, sel, list(args) + [recv])]
            self.assertEqual(len(sols[:1]), 1, sel)
            return sols[0]
        (prog,) = one(K.ClassRef('simpos##b3_boot'), 'create', K.Var())
        one(prog, 'invoke')
        s = sl(prog)
        child, cprog = s['child'], s['child_program']
        c = sl(cprog)
        # the child ran in its own process, with its program on top of that
        # process's stack (TM-100 p6), its parent the boot process
        self.assertEqual(child.cid, 'simpos##process')
        self.assertIs(c['seen_p'], child)
        self.assertIs(c['seen_top'], cprog)
        boot = c['seen_parent']
        self.assertEqual(boot.cid, 'simpos##boot_process')
        # the parent's :get returned the child's :put
        self.assertEqual(s['got'], K.Atom('created'))
        # the boot process was ready (under the supervisor) after its get
        self.assertEqual(s['status_after'], K.Atom('ready'))
        # afterwards the child's program has ended: the printed resign/1
        # let it die (status nil), its stack empty
        cs = sl(child)
        self.assertEqual(cs['status'], K.Atom('nil'))
        self.assertEqual(len(one(cs['invocation_stack'], 'empty')), 0)
        # contexts: the boot process's is number 0, the child's 1; the
        # child's entry is {Program, invoke} (OURS) and it is active
        bs = sl(boot)
        # step 3k: create/3 sends :add_child (INTERPOLATED), so the child
        # is among the boot process's children
        self.assertEqual(self._walk(m.get_slot(bs['children_processes'], 'elements')), [child])
        self.assertEqual(sl(bs['context'])['number'], 0)
        cc = sl(cs['context'])
        self.assertEqual((cc['number'], cc['state']), (1, K.Atom('active')))
        self.assertIs(K.deref(cc['entry'].args[0]), cprog)
        # the ready queue: the child (added by activate/2; dead, it is not
        # taken out, since die/1 does not, and the dispatcher skips it),
        # then the boot process (taken out by the printed suspend/2, put
        # back at the end by the printed resume/2)
        self.assertEqual(m.ready_processes(), [child, boot])

        # status/3: dormant -> on_activate on a fresh process; a mismatch
        # fails and changes nothing (pseudo_pe_process $or$5/2 @3a9-3bc
        # needs the failure)
        areas = K.Cons(K.Atom('free'), K.Cons(K.Atom('free'), K.Cons(K.Atom('free'), K.Cons(
            K.Atom('free'), K.Atom('[]')))))
        (p3, _a) = one(K.ClassRef('simpos##process'), 'create', K.Var(), areas)
        m.reset()
        self.assertFalse(any(True for _ in m.solve_send(p3, 'status', [K.Atom('ready'), K.Atom('x'), p3])))
        self.assertEqual(sl(p3)['status'], K.Atom('dormant'))
        one(p3, 'status', K.Atom('dormant'), K.Atom('on_activate'))
        self.assertEqual(sl(p3)['status'], K.Atom('on_activate'))
        # so a second activate/2 fails at status/3 (the printed activate/2
        # has one clause)
        m.reset()
        self.assertFalse(any(True for _ in m.solve_send(p3, 'activate', [cprog, p3])))
        # clear_masks/1 (the printed activate/2's call): no mask nesting left
        m.set_slot(p3, 'mask_count', 3)
        one(p3, 'clear_masks')
        self.assertEqual(sl(p3)['mask_count'], 0)

        # step 3k: the printed create/2 with its PROCESS line CORRECTED to
        # Class (process.esp, the printed text kept in its comment) runs
        # the printed create_core/3: a dormant process whose parent is the
        # boot process, entered in the class slot instance_array (a heap
        # vector of 63 made by boot_process create/2, OURS) at its
        # context's number; the boot process is element 0.  create/3
        # (INTERPOLATED) makes no entry, so element 1 (the child) stays 0.
        # Injection, observed (2026-11-25): K13 the line put back as
        # printed (PROCESS): this test ERROR, nothing else.  K14 no
        # instance_array entry for the boot process: this test FAIL,
        # nothing else.  K15 any other request/3 succeeds silently: this
        # test FAIL, nothing else.  (The other-request check is the
        # release section below.)
        (p4,) = one(K.ClassRef('simpos##process'), 'create', K.Var())
        self.assertEqual((p4.cid, sl(p4)['status']), ('simpos##process', K.Atom('dormant')))
        self.assertIs(sl(p4)['parent_process'], boot)
        arr = K.deref(m.get_slot(K.ClassRef('simpos##process'), 'instance_array'))
        self.assertEqual(len(arr.args), 63)
        self.assertIs(K.deref(arr.args[0]), boot)
        self.assertEqual(K.deref(arr.args[1]), 0)
        self.assertIs(K.deref(arr.args[sl(sl(p4)['context'])['number']]), p4)

        # held pimmcsp##pseudo_pe_process release/1 @177-189: a dormant PE
        # process passes status/3 (dormant -> on_release) and reaches the
        # boot process's request/3; with status nil it fails.  Until step
        # 3k request/3 was refused; since step 3k (boot_process.esp,
        # INTERPOLATED) the boot process runs the PE process's held
        # release_core/1 (@1cf, $or$2/1 @33b-367): the context is taken
        # from the process and released, three control-block words are
        # cleared (blt 94, INFERENCE), the process leaves its parent's
        # children (remove_child/2, $or$3/1) and its parent, world and
        # user become nil.  The PE process is made here by new/2 (OURS
        # set-up: its held create/3 is not run), given a context and the
        # boot process as parent, as create_core/3 would
        # Injections, observed (2026-11-25, step 3k; from a backup,
        # restored by copy, cmp clean): see test_step3k_b4.
        pe = K.make_instance(m, 'pimmcsp##pseudo_pe_process')
        m.reset()
        self.assertFalse(any(True for _ in m.solve_send(pe, 'release', [pe])))
        (_n, _s, pctx) = one(K.ClassRef('simpos##context'), 'create', K.Var(), K.Var(), K.Var())
        m.set_slot(pe, 'context', pctx)
        m.set_slot(pe, 'parent_process', boot)
        one(boot, 'add_child', pe)
        self.assertIn(pe, self._walk(m.get_slot(sl(boot)['children_processes'], 'elements')))
        m.set_slot(pe, 'status', K.Atom('dormant'))
        m.pcb = {}
        one(pe, 'release')
        ps = sl(pe)
        self.assertEqual(ps['status'], K.Atom('on_release'))
        self.assertEqual((ps['context'], ps['parent_process'], ps['world'], ps['user']),
                         (K.Atom('nil'),) * 4)
        self.assertEqual(sl(pctx)['state'], K.Atom('released'))
        n = sl(pctx)['number']
        self.assertEqual(m.pcb, {(n, 24): 0, (n, 8): 0, (n, 12): K.Atom('nil')})
        kids = m.get_slot(sl(boot)['children_processes'], 'elements')
        self.assertNotIn(pe, [K.deref(k) for k in self._walk(kids)])
        # any other request refuses loudly
        m.reset()
        with self.assertRaises(K.Refusal) as cm:
            any(True for _ in m.solve_send(boot, 'request', [K.Atom('other'), pe, boot]))
        self.assertIn('unsupported_request', cm.exception.detail)

        # every process waits: the boot program waits on an empty stream
        # with nothing else ready (wait/1's second clause)
        (prog2,) = one(K.ClassRef('simpos##b3_boot'), 'create', K.Var())
        m.class_slots, m.saved = {}, {}
        m.set_slot(prog2, 'wait', 1)
        m.reset()
        with self.assertRaises(K.Refusal) as cm:
            any(True for _ in m.solve_send(prog2, 'invoke', [prog2]))
        self.assertEqual(cm.exception.cause, 'would suspend')
        self.assertIn('no process is ready', cm.exception.detail)

        # the 64th context is not made (TR-055 p5: 63 contexts)
        m.class_slots = {}
        for k in range(63):
            one(K.ClassRef('simpos##context'), 'create', K.Var(), K.Var(), K.Var())
        m.reset()
        self.assertFalse(any(True for _ in m.solve_send(
            K.ClassRef('simpos##context'), 'create', [K.Var(), K.Var(), K.Var(), K.ClassRef('simpos##context')])))

    @staticmethod
    def _walk(t):
        out, t = [], K.deref(t)
        while isinstance(t, K.Cons):
            out.append(K.deref(t.args[0]))
            t = K.deref(t.args[1])
        return out

    B4_PROBES = '''class b4_boot has
nature as_boot_program;
instance
attribute r1, r2, req := 0;
:goal(Prog) :-
    :create(#boot_process, B),
    :activate(B, Prog),
    :create(#stream, Out),
    :create_timer(#b4_timer, Out, A1, A2, 16, A4, A5, A6, A7),
    :get(Out, R1), Prog!r1 := R1,
    request(Prog!req, Out, Prog);
local
request(0, _, _) :- !;
request(M, Out, Prog) :- Dev = #b4_timer!last, :input_stream(Dev, In), :put(In, M),
    :get(Out, R2), Prog!r2 := R2;
end.
class b4_timer has
nature pimfep##pimos_timer;
attribute last := 0;
:create(Class, Dev) :- :new(Class, Dev), Class!last := Dev;
end.'''

    def test_step3j_fep_device(self):
        # step 3j: a held FEP device creator run to its end under the
        # supervisor.  pimfep##pimos_timer create_timer/9 (@19-58) makes the
        # device and its process (process/4, create/3), activates it with
        # the printed activate/2 (@48), and then waits, :get on the device's
        # creation-status stream (@4c), for `normal` (@4e-4f) before it puts
        # the creation reply on the caller's stream (reply_message/2 @58).
        # The census stops these creators at the ready queue (its process is
        # not under the supervisor); here the boot program (OURS probe) comes
        # under it first.  b4_timer is an OURS subclass of the held
        # pimos_timer whose create/2 also records the device, so that the
        # probe can reach its input stream; every other method is held.
        # Injections, observed (2026-11-25, as in test_step3j_supervisor):
        #   J3, J4, J5, J7 (no switch on yield; entry {Program, goal}; boot
        #   activate/2 not queued; `current` not set): this test and
        #   test_step3j_supervisor ERROR, nothing else.
        ts, failed = espc.compile_text(self.B4_PROBES, 'simpos')
        self.assertFalse(failed)
        lib = K.load_six()
        for t in list(self.ts) + ts:
            lib.add(t)
        m = K.Machine(lib, max_steps=400000)
        sl = lambda o: {e.name.split('$')[-1]: K.deref(v)
                        for e, v in zip(m.lib.build(o.cid).instance_slots, o.slots)}
        (prog,) = K.call_class_method(m, 'simpos##b4_boot', 'create', [K.Var()])[0]
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(prog, 'invoke', [prog])))
        # the creation reply {16, 1} reached the boot program: the device
        # process ran its held goal/1 and put `normal`
        self.assertEqual(sl(prog)['r1'].codes(), [16, 0, 1, 0])
        # the device process now waits in see/2 on the device's input
        # stream (step 3g's interpolated see/2), suspended, the device on
        # top of its stack
        ((dp, _regs),) = m.saved.values()
        dev = m.get_slot(K.ClassRef('simpos##b4_timer'), 'last')
        d = sl(dp)
        self.assertEqual((dp.cid, d['status']), ('simpos##process', K.Atom('suspended')))
        self.assertIs(d['suspend_reason'], sl(dev)['input_stream'])
        self.assertIs(K.resolve(m.get_slot(d['invocation_stack'], 'elements')).args[0], dev)
        self.assertEqual(sl(dev)['device_id'], 16)
        # a request (OURS: close, code 60, as a 32-bit string, the type
        # disassemble/3 @93 requires) is taken by the device process.
        # Until step 3k it stopped at blt 6f (list_to_vector); step 3k's
        # B4 run of this request and of get_count and get_date_time is
        # test_step3k_b4

    def b4_run(self, code, setup=None):
        # step 3k: the B4 probe (B4_PROBES) on a fresh machine: the boot
        # program comes under the supervisor, makes a timer with the held
        # create_timer/9, then puts one request on the device's input
        # stream and :gets the reply.  -> (machine, program slots)
        ts, failed = espc.compile_text(self.B4_PROBES, 'simpos')
        self.assertFalse(failed)
        lib = K.load_six()
        for t in list(self.ts) + ts:
            lib.add(t)
        m = K.Machine(lib, max_steps=400000)
        (prog,) = K.call_class_method(m, 'simpos##b4_boot', 'create', [K.Var()])[0]
        m.class_slots, m.saved = {}, {}
        if setup:
            setup(m)
        req = K.Str('', 32)
        req.set_codes([16, 0, code, 0])
        m.set_slot(prog, 'req', req)
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(prog, 'invoke', [prog])))
        sl = {e.name.split('$')[-1]: K.deref(v)
              for e, v in zip(m.lib.build(prog.cid).instance_slots, prog.slots)}
        return m, sl

    def test_step3k_b4(self):
        # step 3k, docs/simpos/boot_route.md B4: a request to the timer
        # device process round-trips through the device under the
        # supervisor.  The boot program (OURS probe) comes under the
        # supervisor, the held pimos_timer create_timer/9 makes the device
        # and its process, and a request put on the device's input stream
        # is taken by the device's own process (held loop_main/1, refute/3,
        # fep_message_assembler disassemble/3 with blt 6f), handled by the
        # held command method and answered on the output stream (held
        # reply_message/2, assemble/3), which resumes the boot process.
        # The requests are PIMOS's timer commands (docs/fep_services.md
        # §2.4): 60 close, 301 get_count, 304 get_date_time.  The replies
        # are what PIMOS reads (§2.4, §6.2): {Id, 1}; {Id, 1, Count};
        # {Id, 1, Date, Time}, an integer argument after a length word -1
        # (scsi_fep.kl1:429-445).  The clock values are OURS (the stand-in
        # time and date_time read class slots; no clock is modelled).
        # Injections, observed (2026-11-25; each from a backup copy,
        # restored by copy, cmp clean):
        #   K1 list_to_vector swaps V and Tail (kl0.py): this test and
        #      test_step3g_stream_see ERROR; test_kl0 test_list_to_vector
        #      FAIL; nothing else.
        #   K2 list_to_vector builds a heap vector: test_kl0
        #      test_list_to_vector FAIL, nothing else (this file OK).
        #   K3 put_integer not sign-extended (u16 as before): this test
        #      ERROR, test_step3f_census_recipes FAIL; test_kl0
        #      test_census FAIL; nothing else.
        #   K4 resolve_value returns deref(t), uncopied: this test ERROR,
        #      test_step3j_supervisor FAIL, nothing else.
        #   K5 boot_process request/3 release does nothing:
        #      test_step3j_supervisor FAIL, nothing else.
        #   K6 date_time get_count/3 returns Time, Date: this test FAIL,
        #      nothing else.
        #   K7 set_pcb_entry does not record: test_step3j_supervisor FAIL,
        #      nothing else.
        #   K8 remove_child/2 a no-op: test_step3j_supervisor FAIL,
        #      nothing else.
        #   K9 context release/1 a no-op: test_step3j_supervisor FAIL,
        #      nothing else.
        #   K10 time now/2 ignores the clock: this test FAIL, nothing else.
        #   K11 a negative 32-bit string element not masked: this test
        #      FAIL, nothing else.
        #   K12 create/3 without add_child: test_step3j_supervisor FAIL,
        #      nothing else.
        #   test_kl0.py stayed OK in K4-K12.
        # 60 close: {16, 1}; the device process resigns its program and
        # dies (status nil); the boot process ends after its get
        m, s = self.b4_run(60)
        self.assertEqual(s['r1'].codes(), [16, 0, 1, 0])
        self.assertEqual(s['r2'].codes(), [16, 0, 1, 0])
        self.assertEqual(m.saved, {})
        # 301 get_count: {16, 1, Count}, Count after the length word -1
        m, s = self.b4_run(301, lambda m: m.set_slot(K.ClassRef('simpos##time'), 'clock', 1234))
        self.assertEqual(s['r2'].codes(), [16, 0, 1, 1, 0xffffffff, 1234])
        # the device process goes back to see/2 on its input stream,
        # suspended, and the boot process is ready again: the ready queue
        # kept it (step 3k's slot-store fix, kl0 resolve_value)
        ((dp, _regs),) = m.saved.values()
        self.assertEqual((dp.cid, m.get_slot(dp, 'status')), ('simpos##process', K.Atom('suspended')))

        def dt(m):
            m.set_slot(K.ClassRef('simpos##date_time'), 'date', 33000)
            m.set_slot(K.ClassRef('simpos##date_time'), 'time', 45678)
        # 304 get_date_time: {16, 1, Date, Time}: two length words, then
        # the two integers in the order of get_count(D, Date, Time)
        m, s = self.b4_run(304, dt)
        self.assertEqual(s['r2'].codes(), [16, 0, 1, 2, 0xffffffff, 0xffffffff, 33000, 45678])

    def fs_machine(self, extra=''):
        # step 3l: the stand-ins (and EXTRA, OURS probes) on a fresh machine
        # with the file system of psi/simpos_fs.py mounted (OURS population
        # from the HELD psdpim archive and its HELD INSTALL placement)
        lib = K.load_six()
        ts = []
        if extra:
            ts, failed = espc.compile_text(extra, 'simpos')
            self.assertFalse(failed)
        for t in list(self.ts) + ts:
            lib.add(t)
        m = K.Machine(lib, max_steps=600000)
        FS.mount(m)
        return m

    @staticmethod
    def run_local(m, cid, off, args):
        # a held local predicate at @OFF run alone: its first solution's
        # arguments, 'fail', or ('refused', cause, detail)
        m.reset()
        try:
            for _ in m.solve((m.code(cid), off), args):
                return [K.resolve(a) for a in args]
        except K.Refusal as e:
            return ('refused', e.cause, e.detail)
        return 'fail'

    def test_step3l_b5(self):
        # step 3l, docs/simpos/boot_route.md B5: the directory.  The tree is
        # psi/simpos_fs.py's (OURS population; placement and contents HELD:
        # psdpim/INSTALL and the archive's members); retrieve/3 and /4 are
        # kl0 models (INTERPOLATED from the printed interfaces, TR-056 PDF
        # p22-p23, TR-524 PDF p9, p36-p37, and the held call sites); the
        # nodes are standin/directory.esp and binary_file.esp.
        # Injections, observed (2026-11-25, re-run at the step 3l window
        # commit fb5187d5 so later tests count; each from a backup copy,
        # restored by copy, cmp clean):
        #   L1 fs_walk ignores an explicit version (kl0.py): this test FAIL,
        #      nothing else.
        #   L2 a miss succeeds with the parent directory (kl0.py fs_walk
        #      returns the last node found): this test, test_step3l_b7 and
        #      test_step3l_b6_b8 FAIL, nothing else.
        #   L3 a file's full name without its version (simpos_fs.py
        #      mount): this test, test_step3l_b7 and test_step3l_b6_b8
        #      FAIL, nothing else.
        #   L4 binary_file not_directory/1 fails: this test FAIL, nothing
        #      else.
        #   L5 node_full_name/3 succeeds for any name
        #      (network_node_name.esp): this test, test_fep_census and
        #      test_step3f_census_recipes FAIL (the census row
        #      set_default_node/2 succeeds on its unbound name), nothing
        #      else.
        #   test_kl0.py stayed OK in L1-L5.
        D = K.ClassRef('simpos##directory')
        m = self.fs_machine()

        def retrieve(path, n=4):
            m.reset()
            obj, full = K.Var(), K.Var()
            regs = [obj, K.Str(path)] + ([full] if n == 4 else []) + [D]
            for _ in m.solve_send(D, 'retrieve', regs):
                return K.deref(obj), (K.deref(full).text if n == 4 else None)
            return None
        # the HELD login.com is at me: (>sys>user>pmpsi, INFERENCE), its
        # first line the stamp of the copy it was made from
        f, full = retrieve('>sys>user>pmpsi>login.com')
        self.assertEqual(f.cid, 'simpos##binary_file')
        self.assertEqual(full, '>sys>user>pmpsi>login.com.1')
        text = FS.text_of(m.get_slot(f, 'contents').codes())
        self.assertTrue(text.startswith('% icpsi277::>sys>csp>INSTALL.DIR>login.com.8,'), text[:60])
        self.assertIn('{"Login PIMOS", pimfep##pimos_login_requester}', text)
        self.assertEqual(m.get_slot(f, 'size'), 2448)
        # an explicit version; a version not held; a directory (no version)
        self.assertIs(retrieve('>sys>user>pmpsi>login.com.1')[0], f)
        self.assertIsNone(retrieve('>sys>user>pmpsi>login.com.2'))
        d, dfull = retrieve('>sys>csp>INSTALL.DIR')
        self.assertEqual((d.cid, dfull), ('simpos##directory', '>sys>csp>INSTALL.DIR'))
        self.assertEqual(retrieve('>sys>csp>INSTALL.DIR>pimfep.ptf', 3)[0].cid, 'simpos##binary_file')
        # a miss fails (the held callers' fallback clauses), as does a
        # path through a file or with an empty component
        for miss in ('>sys>user>pmpsi>nope.com', '>sys>user>pmpsi>login.com>x', '>sys>>csp',
                     'pimos:pimfep.image', 'login.com'):
            self.assertIsNone(retrieve(miss), miss)
        # the root (TR-056 PDF p22's printed :root(#directory, Root))
        m.reset()
        (root,) = K.call_class_method(m, 'simpos##directory', 'root', [K.Var()])[0]
        self.assertEqual(m.get_slot(root, 'full_name').text, '>')
        # held pimfep##pimos_file local check_file_size/1 @3d1: retrieve/3,
        # not_directory/1, size/2, size >= 1
        pf = 'pimfep##pimos_file'
        self.assertNotEqual(self.run_local(m, pf, 0x3d1, [K.Str('>sys>user>pmpsi>login.com')]), 'fail')
        self.assertEqual(self.run_local(m, pf, 0x3d1, [K.Str('>sys>csp>PIMOS.DIR')]), 'fail')
        self.assertEqual(self.run_local(m, pf, 0x3d1, [K.Str('>sys>nope')]), 'fail')
        # held pimos_fep_superviser local full_pathname/1 @1bc: clause 1
        # misses "pimos:pimfep.image" (no world defines pimos: yet, and the
        # image is not in the archive), so clause 2 asks the coordinator
        # for an image file name: until B6 (test_step3l_b6_b8) that send
        # refused (class not loaded); now no login file was read, the
        # coordinator has no such item, and full_pathname/1 fails
        r = self.run_local(m, 'pimfep##pimos_fep_superviser', 0x1bc, [K.Var()])
        self.assertEqual(r, 'fail')
        # held pimfep##net_spawn_user set_default_node/2 @29-36 with this
        # node's name (network_node_name's "psi", OURS): its full name is
        # stored; another name fails (INFERENCE: get_your_node/3's later
        # clauses take it as an IP address)
        m.reset()
        self.assertEqual(len(K.call_class_method(m, 'pimfep##net_spawn_user', 'set_default_node',
                                                 [K.Str('psi')])), 1)
        self.assertEqual(m.get_slot(K.ClassRef('pimfep##net_spawn_user'), 'default_spawn_node').text, 'psi')
        m.reset()
        self.assertEqual(K.call_class_method(m, 'pimfep##net_spawn_user', 'set_default_node',
                                             [K.Str('10.1.2.3')]), [])
        # nothing mounted: refused loudly
        m.class_slots = {}
        m.reset()
        with self.assertRaises(K.Refusal) as cm:
            any(True for _ in m.solve_send(D, 'retrieve', [K.Var(), K.Str('>sys'), D]))
        self.assertIn('no file system is mounted', cm.exception.detail)

    def login(self, m, name='pmpsi', password='pmpsi'):
        # step 3l, B7: the held pimfep##simpos_user create/4 (identify,
        # world, "me" := ["user:NAME"], default "me") and setup_process/2
        # on the calling process.  -> (simpos_user, process) or None
        m.reset()
        r = K.call_class_method(m, 'pimfep##simpos_user', 'create', [K.Str(name), K.Str(password), K.Var()])
        if not r:
            return None
        su = r[0][2]
        m.reset()
        (p,) = K.call_class_method(m, 'simpos##process', 'self', [K.Var()])[0]
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(su, 'setup_process', [p, su])))
        return su, p

    def test_step3l_b7(self):
        # step 3l, docs/simpos/boot_route.md B7: login.  The held
        # pimfep##simpos_user create/4 and setup_process/2 run to their ends
        # on the stand-ins user, world and password_list (INTERPOLATED from
        # those held sends; the registry, the password and the rank OURS)
        # and pathname append/4 (HELD-SOURCE, its CESP conversion replaced
        # by an INFERENCE).  The logged-in process's world then resolves
        # `me:` (directory_retrieve, step 3l B5).
        # Injections, observed (2026-11-25, re-run at fb5187d5; each from
        # a backup copy, restored by copy, cmp clean):
        #   M1 identify/4 ignores the password (user.esp): this test FAIL,
        #      nothing else.
        #   M2 define/3 appends instead of prepending, so a redefinition
        #      does not shadow (world.esp): this test FAIL, nothing else.
        #   M3 retrieve ignores the world's default logical name (kl0.py):
        #      this test FAIL, nothing else.
        #   M4 pathname append/4 back to the port's convert_to_8: this test
        #      ERROR (cesp##string not loaded), test_step3l_b6_b8 and
        #      test_step3l_b8_prompt FAIL (login refused), nothing else.
        #   test_kl0.py stayed OK in M1-M4.
        m = self.fs_machine()
        D = K.ClassRef('simpos##directory')

        def full_name(path):
            m.reset()
            f = K.Var()
            for _ in m.solve_send(D, 'retrieve', [K.Var(), K.Str(path), f, D]):
                return K.deref(f).text
            return None
        # before login: no world, so me: and a bare name miss
        self.assertIsNone(full_name('me:login.com'))
        self.assertEqual(full_name('user:pmpsi>login.com'), '>sys>user>pmpsi>login.com.1')
        # a wrong password: identify/4 fails, so create/4 fails
        self.assertIsNone(self.login(m, password='wrong'))
        self.assertIsNone(self.login(m, name='nobody'))
        su, p = self.login(m)
        self.assertEqual(su.cid, 'pimfep##simpos_user')
        u = m.get_slot(p, 'user')
        self.assertEqual((u.cid, m.get_slot(u, 'name').text), ('simpos##user', 'pmpsi'))
        w = m.get_slot(p, 'world')
        self.assertIs(m.get_slot(su, 'world'), w)
        self.assertEqual(m.get_slot(w, 'default').text, 'me')
        pl = m.get_slot(p, 'password_list')
        self.assertEqual(m.get_slot(pl, 'access_mode'), K.Atom('general'))
        self.assertEqual([x.text for x in self._walk(m.get_slot(pl, 'passwords'))], ['pmpsi'])
        # the printed class form :world(#process, W) (TR-056 PDF p25)
        m.reset()
        self.assertIs(K.call_class_method(m, 'simpos##process', 'world', [K.Var()])[0][0], w)
        m.reset()
        self.assertIs(K.call_class_method(m, 'simpos##user', 'user', [K.Var()])[0][0], u)
        # me: = user:pmpsi = >sys>user>pmpsi; a bare name is under me:
        self.assertEqual(full_name('me:login.com'), '>sys>user>pmpsi>login.com.1')
        self.assertEqual(full_name('login.com'), '>sys>user>pmpsi>login.com.1')
        self.assertEqual(full_name('me:'), '>sys>user>pmpsi')
        self.assertIsNone(full_name('pimos:pimfep.image'))
        # a later define shadows an earlier one (login.com redefines "me")
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(
            w, 'define', [K.Str('me'), K.Cons(K.Str('>sys>csp'), K.NIL), w])))
        self.assertEqual(full_name('me:INSTALL.DIR'), '>sys>csp>INSTALL.DIR')
        self.assertIsNone(full_name('me:login.com'))

    B8_PROBES = '''class b8_boot has
nature as_boot_program;
instance
attribute events := 0;
:goal(Prog) :-
    :create(#boot_process, B), :activate(B, Prog),
    :create(#pimfep##simpos_user, "pmpsi", "pmpsi", SU),
    :self(#process, P), :setup_process(SU, P),
    :start(#coordinator),
    put_events(Prog!events),
    :create(#stream, Idle), :get(Idle, _);
local
put_events([]) :- !;
put_events([E|Es]) :- :put(#coordinator!events, E), put_events(Es);
end.'''

    def boot_to_top(self, events, probes=None, boot='b8_boot', before=None):
        # step 3l, B2-B8 on one machine: the boot program (OURS probe) comes
        # under the supervisor (B3), logs in as pmpsi with the held
        # simpos_user create/4 and setup_process/2 (B7), starts the
        # coordinator process (B6, OURS), puts EVENTS on the coordinator's
        # stream (OURS: standing in for the mouse and the menu's answer)
        # and waits for ever on a stream of its own.  -> (machine, the
        # refusal that ended the run).  PROBES, BOOT: another boot program
        # (step 3m); BEFORE(m) runs on the machine before the boot
        m = self.fs_machine(self.B8_PROBES if probes is None else probes)
        if before:
            before(m)
        (prog,) = K.call_class_method(m, 'simpos##' + boot, 'create', [K.Var()])[0]
        t = K.NIL
        for e in reversed(events):
            t = K.Cons(e, t)
        m.set_slot(prog, 'events', t)
        m.reset()
        with self.assertRaises(K.Refusal) as cm:
            any(True for _ in m.solve_send(prog, 'invoke', [prog]))
        return m, cm.exception

    @staticmethod
    def jstr(text):
        s = K.Str('')
        s.text = text
        return s

    def test_step3l_b6_b8(self):
        # step 3l, docs/simpos/boot_route.md B6 and B8: from the boot process
        # to a program started from the system menu.  The coordinator
        # (standin/coordinator.esp, coordinator_program.esp: OURS, labelled)
        # reads the HELD login.com through standard_input_file gett/2 (the
        # reader OURS, psi/esp_reader.py), applies its `define` to the
        # world, holds its `menu` columns and answers information/3.  On
        # `invoke_system_menu` (the printed translation-table action, TR-046
        # PDF p28) and {select, "Login PIMOS"} (OURS) it starts the item's
        # class in a new process the way TM-134 p71 prints: create, create
        # (#process), activate.  The held pimfep##pimos_login_requester then
        # runs in that process (to its prompt: test_step3l_b8_prompt).
        # Injections, observed (2026-11-25, re-run at fb5187d5; each from
        # a backup copy, restored by copy, cmp clean):
        #   N1 gett/2 does not advance (kl0.py): this test and
        #      test_step3l_b8_prompt ERROR (kl0.StepLimit 600001: the login
        #      file is read for ever), nothing else.
        #   N2 a `define` item is taken as a user item (coordinator.esp):
        #      this test FAIL (pimos: unresolved), nothing else.
        #   N3 a select searches the menu, shown or not (coordinator.esp,
        #      the guard dropped too): this test FAIL (the no-menu select
        #      started a process), nothing else.
        #   N4 the reader's atoms without `##` (esp_reader.py): this test
        #      and test_step3l_b8_prompt FAIL (the reader refuses at `##`),
        #      nothing else.
        #   N5 information/3 succeeds with [] for an absent key
        #      (coordinator.esp): this test FAIL, nothing else.
        #   test_kl0.py stayed OK in N1-N5.
        login = self.jstr('Login PIMOS')
        m, r = self.boot_to_top([K.Atom('invoke_system_menu'), K.Vec([K.Atom('select'), login])])
        # the stop: until the window stand-ins (test_step3l_b8_prompt) the
        # held login requester's initiate/1 stopped at its first window
        # send, :create(#standard_io_window, Opts, W) (@af-b4); now every
        # process waits, the requester's last
        self.assertEqual(r.cause, 'would suspend')
        self.assertIn('no process is ready', r.detail)
        C = K.ClassRef('simpos##coordinator')
        # the login file was read: menu columns, user items, define
        menu = [self._walk(c) for c in self._walk(m.get_slot(C, 'menu'))]
        self.assertEqual([len(c) for c in menu], [7, 3])
        self.assertEqual([K.deref(i.args[0]).text for i in menu[1]],
                         ['Pseudo Multi-PSI', 'Login PIMOS', '(Pseudo)Multi-PSI Installer'])
        self.assertEqual(K.deref(menu[1][1].args[1]), K.Atom('pimfep##pimos_login_requester'))
        m.reset()
        self.assertEqual(K.call_class_method(m, 'simpos##coordinator', 'information',
                                             [K.Atom('package'), K.Var()])[0][1], K.Atom('user'))
        m.reset()
        self.assertEqual(K.call_class_method(m, 'simpos##coordinator', 'information',
                                             [K.Atom('pimos_login_additional_function'), K.Var()]), [])
        D = K.ClassRef('simpos##directory')

        def full_name(path):
            m.reset()
            f = K.Var()
            for _ in m.solve_send(D, 'retrieve', [K.Var(), K.Str(path), f, D]):
                return K.deref(f).text
            return None
        self.assertEqual(full_name('pimos:'), '>sys>csp>PIMOS.DIR')
        self.assertEqual(full_name('sys:PIMM.PARAM'), '>sys>csp>SYSTEM.DIR>PIMM.PARAM.1')
        self.assertEqual(full_name('pmpsi:pimm.MEkbn'), '>sys>csp>PMPSI.DIR>pimm.MEkbn.1')
        # the started process: the coordinator's child, running the
        # requester (on top of its invocation stack), world inherited
        (p,) = self._walk(m.get_slot(C, 'started'))
        self.assertIs(m.running_process(), p)
        cp = m.get_slot(C, 'process')
        self.assertIs(m.get_slot(p, 'parent_process'), cp)
        top = K.deref(K.resolve(m.get_slot(m.get_slot(p, 'invocation_stack'), 'elements')).args[0])
        self.assertEqual(top.cid, 'pimfep##pimos_login_requester')
        self.assertIs(m.get_slot(p, 'world'), m.get_slot(cp, 'world'))
        # the coordinator waits on its stream, the boot process on its own
        self.assertEqual(m.get_slot(cp, 'status'), K.Atom('suspended'))
        # held pimos_fep_superviser full_pathname/1 now finds pimos: (the
        # login file's define) without the image, and the coordinator
        # has no pimfep_superviser_image_file_name item: it fails
        self.assertEqual(self.run_local(m, 'pimfep##pimos_fep_superviser', 0x1bc, [K.Var()]), 'fail')
        # a select with no menu shown starts nothing: every process waits
        m, r = self.boot_to_top([K.Vec([K.Atom('select'), self.jstr('Login PIMOS')])])
        self.assertEqual(r.cause, 'would suspend')
        self.assertIn('no process is ready', r.detail)
        self.assertEqual(m.get_slot(C, 'started'), K.NIL)

    def test_step3l_b8_prompt(self):
        # step 3l, B8 continued: the started pimfep##pimos_login_requester
        # runs its held initiate/1 and read/4 on the stand-ins
        # standard_io_window and font (OURS bodies, held selectors and
        # argument order) and process get_number/3 (INFERENCE), to its
        # first prompt, and waits in the window's read/2 for a FEP node
        # name.  The title is made by the held title_string/1 (symbolizer
        # and string stand-ins).
        # Injections, observed (2026-11-25, at fb5187d5; each from a backup
        # copy, restored by copy, cmp clean; N1, N4 and M4 fail this test
        # too, see their headers):
        #   P1 putl/2 keeps nothing (standard_io_window.esp): this test
        #      FAIL, nothing else.
        #   P2 read/2 succeeds at once with [] (standard_io_window.esp):
        #      this test and test_step3l_b6_b8 FAIL (a 'simpos' refusal
        #      past the prompt, not 'would suspend'), nothing else.
        #   P3 get_number/3 gives 0 (process.esp): this test FAIL ('Pimos
        #      remote login 0'), test_fep_census and
        #      test_step3f_census_recipes FAIL (the requester's census rows
        #      pass get_number: 803 / 830 successes), nothing else.
        #   P4 font create/3 takes (F, Name) (font.esp): this test FAIL
        #      (the window's font is a slot constant), test_fep_census and
        #      test_step3f_census_recipes FAIL (803 / 830), nothing else.
        #   test_kl0.py stayed OK in P1-P4.
        m, r = self.boot_to_top([K.Atom('invoke_system_menu'), K.Vec([K.Atom('select'), self.jstr('Login PIMOS')])])
        self.assertEqual(r.cause, 'would suspend')
        C = K.ClassRef('simpos##coordinator')
        (p,) = self._walk(m.get_slot(C, 'started'))
        self.assertIn('%r is suspended' % (p,), r.detail)
        top = K.deref(K.resolve(m.get_slot(m.get_slot(p, 'invocation_stack'), 'elements')).args[0])
        w = m.get_slot(top, 'window')
        self.assertEqual(w.cid, 'simpos##standard_io_window')
        self.assertEqual([K.deref(x).text for x in self._walk(m.get_slot(w, 'transcript'))],
                         ['Enter FEP node name--------->'])
        self.assertEqual(m.get_slot(w, 'shown'), 1)
        self.assertEqual(m.get_slot(w, 'active'), 1)
        self.assertEqual(m.get_slot(m.get_slot(w, 'font'), 'name').text, 'font:test_11.font')
        self.assertIs(m.get_slot(w, 'label_font'), m.get_slot(w, 'font'))
        n = m.get_slot(m.get_slot(p, 'context'), 'number')
        self.assertEqual(m.get_slot(w, 'title').text, 'Pimos remote login %d' % n)
        opts = self._walk(m.get_slot(w, 'options'))
        self.assertEqual(K.deref(K.deref(opts[1]).args[1]), K.Atom('manipulator'))
        self.assertEqual(m.get_slot(p, 'status'), K.Atom('suspended'))

    @staticmethod
    def keys(*lines):
        # step 3m: the coordinator events for LINES typed, each ended by
        # RETURN (13).  The codes are those of the model's 16-bit strings
        # (kl0 Str.codes, the inverse of ptfdump.ch): JIS X 0208, as the
        # held pool strings "local", "exit", "close" are stored.
        ev = []
        for line in lines:
            for c in K.Str(line).codes() + [13]:
                ev.append(K.Vec([K.Atom('key'), c]))
        return ev

    def login_dialogue(self, *lines, **boot):
        # step 3m: boot to the system menu, start Login PIMOS, type LINES.
        # -> (machine, refusal, requester process, requester, window,
        #     dialogue) where the dialogue is the window's history (OURS)
        # as ('put', text), ('typed', text) and ('event', beep), in order.
        # BOOT: boot_to_top's probes, boot and before
        login = self.jstr('Login PIMOS')
        m, r = self.boot_to_top([K.Atom('invoke_system_menu'), K.Vec([K.Atom('select'), login])]
                                + self.keys(*lines), **boot)
        C = K.ClassRef('simpos##coordinator')
        (p,) = self._walk(m.get_slot(C, 'started'))
        top = K.deref(K.resolve(m.get_slot(m.get_slot(p, 'invocation_stack'), 'elements')).args[0])
        w = m.get_slot(top, 'window')
        out, typed = [], []
        for e in reversed(self._walk(m.get_slot(w, 'history'))):
            if isinstance(e, K.Str):
                out.append(('put', e.text))
            elif isinstance(e, int) and e == 13:
                t = K.Str('')
                t.set_codes(typed)
                out.append(('typed', t.text))
                typed = []
            elif isinstance(e, int):
                typed.append(e)
            else:
                out.append(('event', e))
        return m, r, p, top, w, out

    def test_step3m_keyboard(self):
        # step 3m, docs/simpos/boot_route.md §4.5: keyboard input to a window
        # (OURS path, standard_io_window.esp, coordinator.esp: the
        # coordinator's keyboard stream read by the selected window; read/2
        # a character code, input_data/2, getl/2 to RETURN, echo inhibited
        # around the password) takes the held pimfep##pimos_login_requester
        # through its three prompts (read/4 @dc-12c, check_code/4,
        # read_password/3) and on into as_pimos_login_requester
        # login_request/4: get_fep_address/4 takes "local" as a local login,
        # create_message/3 builds the record (blt 42, 43: kl0_opcodes.tsv),
        # get_socket/3 makes its port (@4b9, standin/port.esp), and with no
        # login server running connect_server/4's
        # :local_server_socket(#pimos_remote_login_server, SS) fails (the
        # held class method @32-38 fails while the slot is `none`): the
        # requester writes "Network error." and waits (test_step3m_local_login
        # runs a server).  Until the port stand-in (step 3m) the run stopped
        # at :create(#simpos##port, P); K1-K5 were observed then.
        # Injections, observed (2026-11-25, re-run on the final step 3m tree;
        # each from a backup copy, restored by copy, cmp clean):
        #   K1 input_data/2 keeps nothing (standard_io_window.esp; the line
        #      becomes "ocal"), K2 the keyboard read before the window's own
        #      queue, K3 inhibit_echo/1 a no-op (the password echoed), K4
        #      getl/2 keeps the RETURN, K5 show/1 does not select the window
        #      (the first read waits for ever): each makes this test and
        #      test_step3m_local_login FAIL, nothing else.
        #   test_kl0.py stayed OK in K1-K5.
        m, r, p, req, w, d = self.login_dialogue('local', 'pimos', 'secret')
        self.assertEqual(d, [('put', 'Enter FEP node name--------->'), ('typed', 'local'),
                             ('put', 'Enter your PIMOS user name-->'), ('typed', 'pimos'),
                             ('put', 'Enter your PIMOS password--->'), ('put', 'Network error.'),
                             ('event', K.Atom('beep')), ('event', K.Atom('beep'))])
        # the password went to the requester's buffer, not to the history:
        # read_password's loop ($or$0/4 @32a-34c) stores each code, RETURN
        # too, and counts it, then stops at 13
        self.assertEqual(m.get_slot(req, 'password_counter'), 7)
        buf = K.deref(m.get_slot(req, 'string_buffer')).codes()
        self.assertEqual(buf[:7], K.Str('secret').codes() + [13])
        self.assertIs(m.get_slot(K.ClassRef('simpos##coordinator'), 'selected'), w)
        self.assertEqual(m.get_slot(w, 'echo'), K.Atom('on'))
        self.assertEqual([t.text for t in self._walk(m.get_slot(w, 'transcript'))], ['Network error.'])
        # no server: the requester has its port and waits for a key
        self.assertEqual(r.cause, 'would suspend')
        self.assertEqual(K.deref(m.get_slot(req, 'socket')).cid, 'simpos##port')
        self.assertEqual(m.get_slot(K.ClassRef('pimfep##pimos_remote_login_server'), 'local_server_socket'),
                         K.Atom('none'))
        # a node that is neither "local" nor known: get_fep_address/4's last
        # clause (@6e9-6ef) writes the error, and wait/1 (@15d-16e) beeps
        # twice, discards pending input and waits for a key (every process
        # waits)
        m, r, p, req, w, d = self.login_dialogue('nowhere', 'pimos', '')
        self.assertEqual(d[-4:], [('put', 'Enter your PIMOS password--->'), ('put', 'Unknown FEP node name.'),
                                  ('event', K.Atom('beep')), ('event', K.Atom('beep'))])
        self.assertEqual(d[1], ('typed', 'nowhere'))
        self.assertEqual(r.cause, 'would suspend')
        self.assertEqual(m.get_slot(w, 'beeps'), 2)
        self.assertEqual(m.get_slot(p, 'status'), K.Atom('suspended'))

    B3M_PROBES = B8_PROBES.replace('b8_boot', 'b3m_boot').replace(
        '    :start(#coordinator),',
        '    :create(#b3m_pimos, PP), :create(#process, P2), :activate(P2, PP),\n'
        '    :start(#coordinator),') + '''
class b3m_pimos has
nature as_program;
attribute last := 0, texts := [];
instance
attribute replier := 0, server := 0, r0 := 0, s0 := 0, ni := 0, stage := 0;
:goal(Prog) :-
    #b3m_pimos!last := Prog,
    :create(#pimfep##pimos_remote_login_replier, R), Prog!replier := R,
    :io(R, 0, "", R0), Prog!r0 := R0,
    :create(#pimfep##pimos_remote_login_server, S), Prog!server := S,
    :io(S, 0, "local", S0), Prog!s0 := S0,
    Prog!stage := listening,
    :io(S, 1, "  ", NI), Prog!ni := NI,
    Prog!stage := answered,
    replies(#b3m_pimos!texts, R),
    Prog!stage := replied;
local
replies([], _) :- !;
replies([{C, T}|Ts], R) :- :io(R, C, T, _), replies(Ts, R);
end.'''

    @staticmethod
    def pimos_texts(texts):
        # step 3m: the probe's replier requests {Command, [ID] ++ Text} (ID 0)
        def before(m):
            out = K.NIL
            for c, text in reversed(texts):
                t = K.Str('')
                t.set_codes([0] + K.Str(text.replace('\n', '')).codes() + ([10] if text.endswith('\n') else []))
                out = K.Cons(K.Vec([c, t]), out)
            m.set_slot(K.ClassRef('simpos##b3m_pimos'), 'texts', out)
        return before

    # PIMOS's replier texts for a login that succeeds, docs/fep_services.md
    # §7 rows 3 and 9 (login.kl1:1007-1010, 1075-1090, 1215-1231)
    PIMOS_OK = [(1, 'Login procedure starts.'), (1, 'OK. Your initial program starts.\n'),
                (1, 'Good luck!\n'), (2, '')]

    def test_step3m_local_login(self):
        # step 3m, docs/simpos/boot_route.md §6: a LOCAL login from the held
        # requester to the held pimfep##pimos_remote_login_server on the same
        # PSI, and PIMOS's answer.  The probe b3m_pimos (OURS) stands in for
        # PIMOS's login.kl1 on the far side of the FEP wire: it makes the held
        # pimos_remote_login_replier and sends it io(0, "") (its initiate/1
        # initiates the held socket table; network_subsystem is not installed,
        # standin/network_subsystem.esp, so no listener), makes the server and
        # sends it io(0, "local") and the held io(1, "  "), whose answer NI is
        # what PIMOS's 620 io(1) gets (fep_services.md §7 rows 1-2), then the
        # replier texts of rows 3 and 9 for a login that succeeds.  The wire
        # itself (fep_message_assembler, the 620 frames) is not run.
        # On the way: the port (standin/port.esp: TM-100 Fig. 3.8's send/3 and
        # out_port, connect/2 both ways), message create/2, alarm_watch
        # on_after/5 and wait_and_return/2 (no clock: no timeout fires),
        # class_object/2 and class_name/2 (kl0 dispatch), and the rows blt 35
        # 36 f4 f5, pmi d6 a8 (kl0_opcodes.tsv).
        # Injections, observed (2026-11-25; each from a backup copy, restored
        # by copy, cmp clean; test_kl0.py OK unless named):
        #   C1 port connect/2 one way, C2 port send/3 to itself, C3
        #   wait_and_return/2 on the peer, C6 class_name/2 with the package,
        #   C9 substring/7 16->8 low byte first, C10 copy_string_elements
        #   rotated, C12 pmi d6 without its cut, C16 subtract into A: this
        #   test FAIL, nothing else.
        #   C4 message create/2 fails, C7 class_object/2 fails: this test,
        #   test_fep_census and test_step3f_census_recipes FAIL (C7 also
        #   test_kl0 test_census).
        #   C5 network_subsystem installed: this test ERROR (network_listener
        #   is lost), test_fep_census FAIL.
        #   C13 multiply adds, C14 divide swapped: this test and
        #   test_step3m_keyboard FAIL (the record's H and L).
        #   C8 pmi a8 truncated to 15 bits, C11 f5 strict, C15 f4 not
        #   strict: test_espc OK (not discriminated here); test_kl0
        #   Step3mRows FAIL (C8 ERROR), which was added for them
        m, r, p, req, w, d = self.login_dialogue('local', 'pimos', '', probes=self.B3M_PROBES,
                                                 boot='b3m_boot', before=self.pimos_texts(self.PIMOS_OK))
        self.assertEqual(d, [('put', 'Enter FEP node name--------->'), ('typed', 'local'),
                             ('put', 'Enter your PIMOS user name-->'), ('typed', 'pimos'),
                             ('put', 'Enter your PIMOS password--->'),
                             ('put', 'Your request is accepted.'),
                             ('put', 'Login procedure starts.'),
                             ('put', 'OK. Your initial program starts.<000a>'),
                             ('put', 'Good luck!<000a>'),
                             ('event', K.Atom('beep')), ('event', K.Atom('beep'))])
        self.assertEqual(r.cause, 'would suspend')
        pp = m.get_slot(K.ClassRef('simpos##b3m_pimos'), 'last')
        self.assertEqual(m.get_slot(pp, 'stage'), K.Atom('replied'))
        self.assertEqual(K.resolve(m.get_slot(pp, 'r0')).codes(), [])
        self.assertEqual(K.resolve(m.get_slot(pp, 's0')).codes(), [])
        # NI against ref/pimm/fep.py's login record (read-only import): the
        # same bytes, with RP the PSI user's password.  fep.LOGIN has RP ''
        # (OURS there); the probe logged in as pmpsi/pmpsi (B7): both OURS,
        # and they differ in RP only
        ni = K.resolve(m.get_slot(pp, 'ni'))
        got = b''.join(c.to_bytes(2, 'big') for c in ni.codes())
        fep = self.fep_module()
        self.assertEqual(got, fep.login_record(**dict(fep.LOGIN, rp='pmpsi')))
        self.assertNotEqual(got, fep.login_record(**fep.LOGIN))
        self.assertEqual(ni.codes()[:6], [0, 5, 5, 5, 5, 0])
        # the requester's last status is normal (its check_status/2 after
        # the close)
        self.assertEqual(m.get_slot(req, 'status'), K.Atom('normal'))
        # a key after the two beeps: wait/1 returns, exit_program/1 kills
        # the window and the requester's process ends
        m, r = self.boot_to_top([K.Atom('invoke_system_menu'),
                                 K.Vec([K.Atom('select'), self.jstr('Login PIMOS')])]
                                + self.keys('local', 'pimos', '', 'x'), probes=self.B3M_PROBES,
                                boot='b3m_boot', before=self.pimos_texts(self.PIMOS_OK))
        (p,) = self._walk(m.get_slot(K.ClassRef('simpos##coordinator'), 'started'))
        self.assertEqual((r.cause, r.detail), ('would suspend', 'no process is ready: <simpos##process> has ended'))
        self.assertEqual(K.resolve(m.get_slot(m.get_slot(p, 'invocation_stack'), 'elements')), K.NIL)

    @staticmethod
    def fep_module():
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'pimm_fep', os.path.join(HERE, '..', 'ref', 'pimm', 'fep.py'))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_step3j_as_resource(self):
        # step 3j: as_resource assign/1, assigned/1, resign/1 (INTERPOLATED:
        # pseudo_scsi create/4 @71, close/1 @150-16d; kappa2 KP_POOL.ESP
        # check_resource :285-290; TM-100's slot `resources`).  The held
        # pseudo_scsi close/1 takes its assigned path only when the calling
        # process holds the scsi.
        # Injection, observed (2026-11-25, as in test_step3j_supervisor):
        #   J6 assigned/1 always succeeds: this test, test_fep_census and
        #   test_step3f_census_recipes FAIL, nothing else.
        #   J11 assign/1 a no-op: this test ERROR, nothing else.
        #   J12 resign/1 a no-op: the same three as J6 FAIL, nothing else.
        m = K.fep_machine()
        sc = K.make_instance(m, 'pimscsi##pseudo_scsi')

        def run(sel):
            m.reset()
            return any(True for _ in m.solve_send(sc, sel, [sc]))
        self.assertFalse(run('assigned'))
        # not assigned: close/1 takes error(soft, not_assigned, ...), which
        # stops at class_object on a pimscsi pool term (pools not relied on)
        m.reset()
        with self.assertRaises(K.Refusal) as cm:
            any(True for _ in m.solve_send(sc, 'close', [sc]))
        self.assertEqual((cm.exception.cause, cm.exception.detail), ('built-in', 'class_object of 1900544'))
        self.assertTrue(run('assign'))
        proc = m.running_process()
        held = K.resolve(m.get_slot(m.get_slot(proc, 'resources'), 'elements'))
        self.assertIs(held.args[0], sc)
        self.assertEqual(held.args[1], K.NIL)
        self.assertTrue(run('assigned'))
        # assigned: close/1's held path sets status closed and resigns
        self.assertTrue(run('close'))
        self.assertEqual(m.get_slot(sc, 'status'), K.Atom('closed'))
        self.assertEqual(K.resolve(m.get_slot(m.get_slot(proc, 'resources'), 'elements')), K.NIL)
        self.assertFalse(run('assigned'))
        self.assertFalse(run('resign'))

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
            # one child: the loop sends it exterminate/1 (not stood in
            # until step 3n).  Step 3n: exterminate/1 is stood in
            # (INTERPOLATED, standin/process.esp) and the child here is the
            # running census process itself: it becomes dead (nil) and the
            # dispatcher, giving the processor away, finds no supervisor
            st = m.get_slot(proc, 'status')
            self.assertEqual(len(self.send(kids, 'add_last', proc)), 1)
            self.assertEqual(exit1(), 'no ready queue (0 (a slot constant)): the supervisor is not started')
            self.assertEqual(m.get_slot(proc, 'status'), K.Atom('nil'))
        finally:
            self.send(kids, 'clear')
            m.set_slot(proc, 'status', st)

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
                # past `initiator`: low_if/2 to include_item_1/3 (@261), the
                # others to the unit check on the census's unbound unit.
                # Step 3h stopped low_if/2 at blt e0 @26b; since step 3i
                # (blt e0 witnessed) the unbound item is neither an integer
                # nor an atom, e1 and e0 both jump, and it fails: unbound
                # probing, not progress
                want = 'failure' if sel == 'low_if/2' else 'unbound argument'
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


class Window(unittest.TestCase):
    """Window milestones M0, M3 (core) and M5 (docs/simpos/
    window_environment_plan.md §5): the font file read, the window
    stand-ins drawing through the display device (psi/windev.py, OURS; the
    window manager is the ESP stand-in standin/window_pane.esp, OURS), and
    the Login PIMOS window as a LIVE run of the held requester draws it.
    The boot helpers are Standins' (step 3l/3m)."""

    @classmethod
    def setUpClass(cls):
        cls.ts = espc.standins()

    fs_machine = Standins.fs_machine
    boot_to_top = Standins.boot_to_top
    _walk = staticmethod(Standins._walk)
    keys = staticmethod(Standins.keys)
    jstr = staticmethod(Standins.jstr)
    pimos_texts = staticmethod(Standins.pimos_texts)
    B8_PROBES = Standins.B8_PROBES
    B3M_PROBES = Standins.B3M_PROBES
    PIMOS_OK = Standins.PIMOS_OK

    def test_win_m0_font(self):
        # M0: psdpim's FONT.DIR placed under font: (simpos_fs.py: HELD
        # INSTALL line, OURS directory >sys>font and alias), and font
        # create/3 reading it through the device (load_font/5, f822).
        # Injections: see test_win_m5_login_screen's header.
        import windev
        import winfb
        pop = {p: n for p, n, _c in FS.population()}
        fonts = sorted(p for p in pop if p.startswith('>sys>font>'))
        self.assertEqual(fonts, ['>sys>font>' + n for n in (
            'csp.icon', 'csppestate.font', 'performance.font', 'test_10.font',
            'test_11.font', 'test_11b.font', 'tiny_7.font')])
        self.assertEqual(FS.raw_of('>sys>font>test_11.font'), winfb.font_bytes())
        m = self.fs_machine()

        def create(name):
            m.reset()
            r = K.call_class_method(m, 'simpos##font', 'create', [K.Str(name), K.Var()])
            return r[0][1] if r else None
        f = create('font:test_11.font')
        self.assertEqual([m.get_slot(f, k) for k in ('id', 'width', 'height')], [0, 11, 14])
        self.assertEqual(m.get_slot(f, 'name').text, 'font:test_11.font')
        # test_11b: same header, different glyphs: a font the command set
        # cannot draw (winfb's freeze: font 0 only) gets an id of its own
        f = create('font:test_11b.font')
        self.assertEqual([m.get_slot(f, k) for k in ('id', 'width', 'height')], [1, 11, 14])
        f = create('font:test_10.font')
        self.assertEqual([m.get_slot(f, k) for k in ('id', 'width', 'height')], [2, 10, 11])
        # a name with no file fails (INFERENCE, the plan's M0 row); a file
        # that is not an f822 font fails too (csp.icon)
        self.assertIsNone(create('font:font_13.font'))
        self.assertIsNone(create('font:csp.icon'))
        # the 'A' of the file the device decoded: the plan §1.4's 48 dots
        fr = windev.device(m).frame
        self.assertEqual(fr.glyph(0, 0x2341, 0, 0, 3), winfb.OK)
        self.assertEqual(fr.count(), 48)

    def pane(self, m, x, y, cols, rows):
        m.reset()
        ((*_, p),) = K.call_class_method(m, 'simpos##window_pane', 'create', [x, y, cols, rows, 0, K.Var()])
        return p

    @staticmethod
    def send(m, obj, sel, *args):
        m.reset()
        return any(True for _ in m.solve_send(obj, sel, list(args) + [obj]))

    @staticmethod
    def jis(codes):
        s = K.Str('')
        s.set_codes(codes)
        return s

    def test_win_pane(self):
        # M3/M5, directed: window_pane.esp (OURS) on the device, alone.
        # The live route never fills its 40 x 7 window, so scrolling, wrap,
        # key#lf/key#cr, the label's cut and the missing-glyph box are
        # pinned here.  Every check reads the FRAMEBUFFER back
        # (windev.read_cells), not a shadow.  Injections: see
        # test_win_m5_login_screen's header.
        import windev
        import winfb
        m = self.fs_machine()
        p = self.pane(m, 100, 50, 10, 3)
        g = {k: m.get_slot(p, k) for k in ('x', 'y', 'w', 'h', 'left', 'top', 'iw', 'ih')}
        # 10 x 3 cells of 11 x 14, 2-dot border, 1-dot margins, a label
        # strip of 16 and a 1-dot rule (window_pane.esp's head)
        self.assertEqual(g, {'x': 100, 'y': 50, 'w': 116, 'h': 65, 'left': 103, 'top': 70,
                             'iw': 110, 'ih': 42})
        fr = windev.device(m).frame

        def text():
            return windev.read_cells(fr, g['left'], g['top'], 10, 3)

        def label():
            return windev.read_cells(fr, g['left'], g['y'] + 3, 10, 1)[0]
        # the empty pane: a 2-dot border and the rule, nothing else
        self.assertEqual(fr.count(), 116 * 65 - 112 * 61 + 112)
        self.assertTrue(self.send(m, p, 'set_title', K.Str('A title longer than the strip')))
        self.assertEqual(label(), 'A title lo')
        self.assertTrue(self.send(m, p, 'select'))
        self.assertEqual(text(), ['#', '', ''])
        self.assertTrue(self.send(m, p, 'put_string', K.Str('Hello')))
        self.assertEqual(text(), ['Hello#', '', ''])
        self.assertTrue(self.send(m, p, 'new_line'))
        # a line longer than the pane goes on in the next row
        self.assertTrue(self.send(m, p, 'put_string', K.Str('abcdefghijklmno')))
        self.assertEqual(text(), ['Hello', 'abcdefghij', 'klmno#'])
        # a newline on the last row scrolls: up one row, the last cleared
        self.assertTrue(self.send(m, p, 'new_line'))
        self.assertEqual(text(), ['abcdefghij', 'klmno', '#'])
        # key#lf (10) inside a string breaks the line; key#cr (13) returns
        self.assertTrue(self.send(m, p, 'put_string', self.jis(
            K.Str('xyz').codes() + [10] + K.Str('qq').codes() + [13] + K.Str('Z').codes())))
        self.assertEqual(text(), ['klmno', 'xyz', 'Z[q]'])
        # a code test_11 lacks (16#2422, hiragana) shows the 0xffff box
        self.assertTrue(self.send(m, p, 'put_code', 0x2422))
        self.assertEqual(text(), ['klmno', 'xyz', 'Z<ffff>#'])
        self.assertEqual(fr.status.count(winfb.MISSING), 1)
        # deselect: the block cursor is erased (xor twice); select again
        self.assertTrue(self.send(m, p, 'deselect'))
        self.assertTrue(self.send(m, p, 'put_code', 0x2341))
        self.assertEqual(text(), ['klmno', 'xyz', 'Z<ffff>A'])
        self.assertTrue(self.send(m, p, 'clear'))
        self.assertEqual(text(), ['', '', ''])
        self.assertEqual(label(), 'A title lo')
        # the device's log is a winfb command stream: replayed, the same frame
        self.assertEqual(winfb.run_stream(windev.device(m).stream_text()).pbm(), fr.pbm())
        self.assertTrue(self.send(m, p, 'erase'))
        self.assertEqual(fr.count(), 0)

    # the live screens: keys typed (None: the password's first three
    # letters, not ended), the window's text read back from the frame, the
    # cursor's cell (col, row)
    SCREENS = {
        'name': (['local'], ['Enter FEP node name--------->', 'local',
                             'Enter your PIMOS user name-->', '#', '', '', ''], (0, 3)),
        'password': (['local', 'pimos', None], ['Enter FEP node name--------->', 'local',
                                                'Enter your PIMOS user name-->', 'pimos',
                                                'Enter your PIMOS password--->', '#', ''], (0, 5)),
        'login': (['local', 'pimos', ''], ['Your request is accepted.', 'Login procedure starts.',
                                           'OK. Your initial program starts.', '', 'Good luck!',
                                           '', '#'], (0, 6)),
    }
    # (sha256 of the frame's PBM, set dots), MEASURED 2026-11-25, with the
    # status band (window M6: 97,756 dots more in every stage, the band
    # and its box naming standard_io_window/1)
    PINS = {
        'name': ('4a31e4ae4ffddcfd377679180525b2cfdcc07cd08f3d666d23bb05ef212d30bb', 102952),
        'password': ('28728b793499409abe820be92455041b85d1bbee03360f5273d3a4ce3645be43', 104021),
        'login': ('c1afaf8cd4050773b32f47d874bc700faa7d34f0caa5487978f66cd024287b17', 103715),
    }
    # M5's pins, before the band: the same frames with the band's rows
    # (944-1023) cleared, so the window's own drawing is unchanged
    M5_PINS = {
        'name': ('d134cbfaa83e9844279330dd13fdfcf6b290c5917c8ca83ed187788eaa248de8', 5196),
        # the same frame as after 'local', 'pimos' alone: the password's
        # letters draw nothing (echo inhibited by the held read/4 @122)
        'password': ('380d5779597c6dbfcb0693e668963f97c2d362970178979a6957132ed42fca44', 6265),
        'login': ('c4e83dfdbe355ecfb4204087dca9561872a31c04caee94e8681fd0a505809350', 5959),
    }

    @staticmethod
    def band(fr, n=20):
        # window M6: the status band read back (status_band.esp): its two
        # rows white on black (read from the inverted frame), the box's
        # name (N cells) black on white
        import windev
        import winfb
        g = winfb.Frame()
        g.rows = [r ^ ((1 << 1280) - 1) for r in fr.rows]
        return (windev.read_cells(g, 8, 952, 30, 1), windev.read_cells(g, 8, 974, 30, 1),
                windev.read_cells(fr, 411, 952, n, 1))

    def screen(self, keys):
        # boot -> system menu -> Login PIMOS -> KEYS, with the 3m probe for
        # PIMOS (OURS) on the far side.  -> (machine, window, device)
        import windev
        ev = [K.Atom('invoke_system_menu'), K.Vec([K.Atom('select'), self.jstr('Login PIMOS')])]
        for k in keys:
            if k is None:
                ev += [K.Vec([K.Atom('key'), c]) for c in K.Str('sec').codes()]
            else:
                ev += self.keys(k)
        m, r = self.boot_to_top(ev, probes=self.B3M_PROBES, boot='b3m_boot',
                                before=self.pimos_texts(self.PIMOS_OK))
        self.assertEqual(r.cause, 'would suspend')
        (p,) = self._walk(m.get_slot(K.ClassRef('simpos##coordinator'), 'started'))
        top = K.deref(K.resolve(m.get_slot(m.get_slot(p, 'invocation_stack'), 'elements')).args[0])
        return m, p, m.get_slot(top, 'window'), windev.device(m)

    def test_win_m5_login_screen(self):
        # M5 (and M3's core): the Login PIMOS window drawn by a LIVE run.
        # The boot of step 3l/3m (B8 probe, coordinator, the held login.com
        # menu) starts the HELD pimfep##pimos_login_requester; its held
        # initiate/1 and read/4 send create/3, set_font/2 (font:test_11.font,
        # now read from the placed HELD file), set_title/2, activate/1,
        # clear/1, show/1, putl/2, read/2, getl/2 to the standard_io_window
        # stand-in, which draws through window_pane.esp (OURS) and the
        # device (OURS) with the HELD font's glyphs.  Nothing here types the
        # strings: the prompts are the requester's pool strings, the replies
        # the 3m probe's (OURS stand-in for PIMOS, fep_services.md §7).
        # What is pinned, per stage: the window's text read back from the
        # frame by glyph matching, its label, its place, the cursor's
        # cell, and the frame's PBM sha256 and dot count; the device's
        # command log replays through winfb.run_stream to the same frame and
        # the PNG (windev.png_bytes) decodes back to it.  psi/winshot.py
        # writes these screens as PNGs.
        # Injections, observed (2026-11-25, before the step 3n merge; each
        # from a backup copy, restored by copy, cmp clean; the whole of
        # test_espc.py and test_kl0.py run each time, test_kl0 OK in all):
        #   W1 window_pane put_char draws every glyph at the row's left edge,
        #      not the cursor's dot (putl ignoring the cursor): the three
        #      stages of this test and test_win_pane FAIL, nothing else.
        #   W2 standard_io_window drawn_title draws nothing (the title
        #      not drawn): the three stages FAIL, nothing else.
        #   W3 windev glyph/6 keeps the code's low byte (a wrong code
        #      mapping: every glyph the 0xffff box): the three stages and
        #      test_win_pane FAIL, nothing else.
        #   W4 window_pane newline scrolls one row early (row + 2 < rows):
        #      the 'login' stage and test_win_pane FAIL, nothing else.
        #   W5 window_pane frame: a 1-dot border (the plan's M5 injection):
        #      the three stages and test_win_pane FAIL, nothing else.
        #   W6 standard_io_window echo draws with echo inhibited (the
        #      password shown): the 'password' stage FAILS, nothing else.
        #   W7 windev cell_of: width and height swapped: test_win_m0_font,
        #      the three stages and test_win_pane FAIL, nothing else.
        #   W8 simpos_fs: no `font` alias: test_win_m0_font ERROR, the three
        #      stages, test_step3l_b8_prompt, test_step3m_keyboard and
        #      test_step3m_local_login FAIL (the requester's font create/3
        #      fails, so its initiate/1 does), nothing else.
        #   W9 window_pane's cursor drawn by set, not exclusive_or (never
        #      erased): the three stages and test_win_pane FAIL, nothing
        #      else.
        # After the merge, test_win_m5_bridged_screen was checked against
        # W1-W9 alone (with test_fep_bridge.py): it FAILS in all but W6
        # (the bridged run's final screen has no password on it); W8 also
        # fails test_fep_bridge Scripted and Tape (the requester stops at
        # its font), test_fep_bridge OK otherwise.
        import windev
        import winfb
        for stage, (keys, lines, cell) in self.SCREENS.items():
            with self.subTest(stage=stage):
                m, p, w, dev = self.screen(keys)
                pane = m.get_slot(w, 'pane')
                g = [m.get_slot(pane, k) for k in ('x', 'y', 'w', 'h', 'cols', 'rows')]
                # 40 x 7 cells of test_11 (the held size option), centred on
                # the 1280 x 944 screen (OURS for the manipulator position)
                self.assertEqual(g, [417, 411, 446, 121, 40, 7])
                self.assertEqual((m.get_slot(pane, 'col'), m.get_slot(pane, 'row')), cell)
                n = m.get_slot(m.get_slot(p, 'context'), 'number')
                fr = dev.frame
                self.assertEqual(windev.read_cells(fr, 420, 414, 40, 1), ['Pimos remote login %d' % n])
                self.assertEqual(windev.read_cells(fr, 420, 431, 40, 7), lines)
                # nothing is drawn outside the window's rectangle and the
                # status band (window M6: rows 944-1023, its box naming
                # the requester's window, selected when shown)
                inside = sum(bin((fr.rows[y] >> (1280 - 417 - 446)) & ((1 << 446) - 1)).count('1')
                             for y in range(411, 411 + 121))
                band = sum(bin(fr.rows[y]).count('1') for y in range(944, 1024))
                self.assertEqual(inside + band, fr.count())
                self.assertEqual(self.band(fr), (['USER : pmpsi'], ['SIMPOS Version V7'],
                                                 ['standard_io_window/1']))
                self.assertEqual(set(fr.status), {winfb.OK})
                self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.PINS.get(stage))
                self.assertEqual(self.without_band(fr), self.M5_PINS.get(stage))
                self.assertEqual(winfb.run_stream(dev.stream_text()).pbm(), fr.pbm())
                self.assertEqual(windev.png_rows(windev.png_bytes(fr)), fr.rows)

    @staticmethod
    def without_band(fr):
        import windev
        import winfb
        g = winfb.Frame()
        g.rows = fr.rows[:944] + [0] * (len(fr.rows) - 944)
        return windev.pbm_sha256(g), g.count()

    # with the status band (window M6): 97,756 dots more than M5's pin,
    # M5_BRIDGED_PIN, which the frame with the band cleared still equals
    BRIDGED_PIN = ('c33da8f127897aea8501f68ae999bcc33dda26df6ec890281b2e29c11007d614', 103724)
    M5_BRIDGED_PIN = ('cd57f0ff7e32029dc432da52be8795f1b2ba3fcb89ca25186304e2eec13ff404', 5968)

    def bridged(self):
        # step 3n's run: the held requester logs into real PIMOS (pimm.py)
        # through the held pimfep, the PIMOS side replayed from the
        # committed tape (psi/fep_bridge.py replay, test_fep_bridge.py Tape)
        import fep_bridge
        stop, psi, left, _t = fep_bridge.replay(os.path.join(HERE, 'fep_bridge_tapes', 'login_pwd.json'))
        self.assertEqual((stop.cause, left), ('would suspend', []))
        return psi.m

    def test_win_m5_bridged_screen(self):
        # M5 on step 3n's bridged run: the same window, now holding PIMOS's
        # OWN replies (login.kl1, through the 620 wire and the held
        # pimos_remote_login_replier), not the 3m probe's.  Only the label's
        # number differs from the 'login' stage (this run's process is 8).
        # The committed PNGs of docs/simpos/screens/ decode to the pinned
        # frames.  Injections: see test_win_m5_login_screen's header (this
        # test FAILS in W1-W5 and W7-W9, OBSERVED; not in W6).
        # Window M6 (2026-11-25): the tape replays with its own user
        # (fep_bridge.tape_script: step 3m's menu select, so the window
        # is centred on the mouse's start, the old place); the frame has
        # the status band now.  M4's tape starts it with the mouse
        # (test_win_m4_console).
        import windev
        import winfb
        m = self.bridged()
        fr = windev.device(m).frame
        (p,) = self._walk(m.get_slot(K.ClassRef('simpos##coordinator'), 'started'))
        top = K.deref(K.resolve(m.get_slot(m.get_slot(p, 'invocation_stack'), 'elements')).args[0])
        pane = m.get_slot(m.get_slot(top, 'window'), 'pane')
        self.assertEqual([m.get_slot(pane, k) for k in ('x', 'y', 'w', 'h', 'cols', 'rows')],
                         [417, 411, 446, 121, 40, 7])
        self.assertEqual(windev.read_cells(fr, 420, 414, 40, 1),
                         ['Pimos remote login %d' % m.get_slot(m.get_slot(p, 'context'), 'number')])
        self.assertEqual(windev.read_cells(fr, 420, 431, 40, 7), self.SCREENS['login'][1])
        self.assertEqual(self.band(fr), (['USER : pmpsi'], ['SIMPOS Version V7'],
                                         ['standard_io_window/1']))
        self.assertEqual(set(fr.status), {winfb.OK})
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.BRIDGED_PIN)
        self.assertEqual(self.without_band(fr), self.M5_BRIDGED_PIN)
        self.assertEqual(winfb.run_stream(windev.device(m).stream_text()).pbm(), fr.pbm())
        self.assert_shots()

    def assert_shots(self):
        # the committed PNGs of docs/simpos/screens/ decode to the pinned
        # frames (psi/winshot.py writes them)
        import windev
        import winfb
        shots = os.path.join(HERE, '..', 'docs', 'simpos', 'screens')
        for name, pin in (('login_pimos_password', self.PINS['password']),
                          ('login_pimos_bridged', self.BRIDGED_PIN),
                          ('pimos_console', self.CONSOLE_PIN),
                          ('system_menu', self.MENU_PINS['boxed'])):
            with open(os.path.join(shots, '%s.png' % name), 'rb') as f:
                g = winfb.Frame()
                g.rows = windev.png_rows(f.read())
            self.assertEqual((windev.pbm_sha256(g), g.count()), pin, name)

    CONSOLE_PIN = ('f9da0fe2881c5bd15fd41c07608396991eec0775a6295faa485f205e602b4a53', 110676)

    def console(self):
        # window M4's run: PIMOS's shell window (104) bridged to the PSI,
        # replayed from the committed tape (test_fep_bridge.py Console)
        import fep_bridge
        stop, psi, left, t = fep_bridge.replay(
            os.path.join(HERE, 'fep_bridge_tapes', 'console_pwd.json'))
        self.assertEqual((stop.cause, left), ('would suspend', []))
        return psi, t

    def test_win_m4_console(self):
        # M4: PIMOS's console window drawn by a run whose every window
        # message is PIMOS's own (pimm.py, through the bridge, replayed
        # from psi/fep_bridge_tapes/console_pwd.json): 104, then 127
        # reshape (200, 200, 47 x 14), 130 "PIMOS CONSOLE", 132
        # font:test_11.font, 143 show, 111 "Shell>> ", 110 getl.  The PSI
        # runs them with the HELD pimfep##pimos_window_process (its
        # create_window/9, window_loop, put/2) and the HELD
        # pimfep##pimos_window / pimos_window_editor (kl1_message/2,
        # reshape, set_title, set_font, show, putb, flush, getl) on the
        # stand-ins pmacs_window, editor_text_buffer, buffer_region,
        # editor_command_interpreter, pmacs_request (OURS/INFERENCE,
        # their headers).  The user (OURS, fep_bridge.shell_events)
        # clicks in the console and types `pwd` RETURN: the getl's answer
        # is the editor's own (getl_from_buffer/3 after carriage_return's
        # after-demon), and PIMOS's reply is drawn after it.
        # Injections, OBSERVED (2026-11-25, after merging master 10884b99;
        # each from a backup copy, restored by copy, cmp clean; run each
        # time: test_espc.py Window, test_fep_bridge.py, test_kl0.py; the
        # rest of the window tests and test_fep_bridge OK unless listed):
        #   J1 kl0 blt 69 not_equal_string always fails: this test,
        #      test_fep_bridge Console.test_replay and test_kl0
        #      Table.test_step3c_cells FAIL.
        #   J2 pmacs_window set_font/2 drops the font (the plan's M4
        #      injection): this test ERROR (the font slot 0), nothing else:
        #      the dots are the same, test_11 being the device's default.
        #   J3 pmacs_window get_interpreter/2 answers the editor (the plan's
        #      M3 injection): this test, test_win_m6_selection and
        #      Console.test_replay FAIL.
        #   J4 standard_editor carriage_return/1 inserts no line end (code
        #      10): this test and Console.test_replay FAIL (the 110 is
        #      never answered).
        #   J5 coordinator: mouse#l on a window does nothing:
        #      test_win_m6_selection FAILS, nothing else.
        #   J6 coordinator: mouse#l selects the newest window, not the one
        #      under the mouse (the plan's M6 injection, in this form):
        #      test_win_m6_selection FAILS, nothing else.
        #   J7 menu_pane: the box drawn by set, not exclusive_or:
        #      test_win_m6_system_menu FAILS, nothing else.
        #   J8 status_band: the band 40 rows high, not 80: this test, the
        #      three stages of test_win_m5_login_screen,
        #      test_win_m5_bridged_screen and test_win_m6_system_menu FAIL.
        #   J9 pmacs_request: the argument read from the stored vector again
        #      (the backtracking bug, pmacs_request.esp's head): this test,
        #      test_win_m6_selection and Console.test_replay FAIL.
        import windev
        import winfb
        psi, t = self.console()
        m = psi.m
        fr = windev.device(m).frame
        C = K.ClassRef('simpos##coordinator')
        ws = self._walk(m.get_slot(C, 'windows'))
        self.assertEqual([w.cid for w in ws], ['pimfep##pimos_window', 'simpos##standard_io_window'])
        pane = m.get_slot(ws[0], 'pane')
        self.assertEqual([m.get_slot(pane, k) for k in ('x', 'y', 'w', 'h', 'cols', 'rows')],
                         [200, 200, 523, 219, 47, 14])
        # 132's font, through the held editor's set_font/4 (blt 69): the
        # window's font is the font object of font:test_11.font, 11 x 14
        # (the device's default is also test_11, so the dots alone would
        # not show a dropped font)
        f = m.get_slot(ws[0], 'font')
        self.assertEqual((f.cid, K.resolve(m.get_slot(f, 'name')).text,
                          m.get_slot(f, 'width'), m.get_slot(f, 'height')),
                         ('simpos##font', 'font:test_11.font', 11, 14))
        self.assertEqual(windev.read_cells(fr, 203, 203, 47, 1), ['PIMOS CONSOLE'])
        self.assertEqual(windev.read_cells(fr, 203, 220, 47, 4), [
            'Shell>> pwd',
            ' The value of task: directory is ">sys>user>pmp',
            'si" .',
            'Shell>> #'])
        self.assertEqual(windev.read_cells(fr, 203, 276, 47, 10), [''] * 10)
        # the login window is where the menu's click put it, untouched
        self.assertEqual(windev.read_cells(fr, 758, 547, 40, 1), ['Pimos remote login 8'])
        # the left button in the console selected it (window M6)
        self.assertIs(m.get_slot(C, 'selected'), ws[0])
        self.assertEqual(self.band(fr, 14), (['USER : pmpsi'], ['SIMPOS Version V7'],
                                             ['pmacs_window/2']))
        # the tape's script (fep_bridge.py): the login by the menu, the
        # shell's line after a click in the login window and one in the
        # console; the keys reach the console only by that last click
        self.assertEqual(t['script']['login'][:2], [['mouse', 'rr', 640, 560], ['mouse', 'l', 978, 605]])
        self.assertEqual(t['script']['shell'], [['mouse', 'l', 900, 620], ['mouse', 'l', 300, 300]]
                         + [['key', c] for c in K.Str('pwd').codes() + [13]])
        self.assertEqual(t['result']['user_at'], [6, 19])
        self.assertEqual((psi.user_at, psi.shell_at), (6, 19))
        self.assertEqual(set(fr.status), {winfb.OK})
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.CONSOLE_PIN)
        self.assertEqual(t['result']['screen'], dict(sha256=self.CONSOLE_PIN[0], dots=self.CONSOLE_PIN[1]))
        self.assertEqual(winfb.run_stream(windev.device(m).stream_text()).pbm(), fr.pbm())
        self.assertEqual(windev.png_rows(windev.png_bytes(fr)), fr.rows)

    def test_win_m6_selection(self):
        # M6: mouse#l selects the window under the mouse, and the keys go
        # to the selected window.  The M4 run's script with the console
        # click left out: the click in the login window selects the
        # requester (its window, under the mouse), so `pwd` goes to it, not
        # to the console: the PSI never answers the console's 110 (no
        # {28, 1, "pwd"}), the console shows no echo, and the requester,
        # its wait/1 answered, exits (the band's box cleared).  PIMOS's
        # side is fed from the tape regardless (its later texts appear
        # unasked).  With mouse#l a no-op, or selecting the newest window
        # whatever is under the mouse, the keys reach the console and
        # this test fails (J5, J6 in test_win_m4_console's header).
        import json
        import fep_bridge as FB
        import windev
        with open(os.path.join(HERE, 'fep_bridge_tapes', 'console_pwd.json')) as f:
            t = json.load(f)
        psi = FB.PsiSide(script=dict(login=t['script']['login'],
                                     shell=[['mouse', 'l'] + list(FB.LOGIN_WINDOW_AT)]
                                     + FB.key_script('pwd')))
        tape, sent = list(t['exchanges']), []

        def exchange(out):
            sent.extend(FB.show(r) for r in out)
            return [bytes.fromhex(r) for r in tape.pop(0)['to_psi']] if tape else []
        self.assertEqual(psi.run(exchange).cause, 'would suspend')
        self.assertNotIn([28, 0, 1, FB.fepm.jis('pwd')], sent)
        fr = windev.device(psi.m).frame
        self.assertEqual(windev.read_cells(fr, 203, 220, 47, 1)[0][:9], 'Shell>>  ')
        C = K.ClassRef('simpos##coordinator')
        self.assertEqual([w.cid for w in self._walk(psi.m.get_slot(C, 'windows'))], ['pimfep##pimos_window'])
        self.assertEqual(psi.m.get_slot(C, 'selected'), 0)

    # window M6: (sha256, dots) of the boot screen with the system menu
    # open at fep_bridge.MENU_AT, and with "Login PIMOS" boxed
    MENU_PINS = {
        'open': ('c1843568e297eab6c6f1db50526a28353e62bb03bd67da654c346e0569a96d3d', 108361),
        'boxed': ('87871fa8e06af511b3e0018c6c1d95fa5e8299063dc8c9c8b88c22fceaaf1706', 109023),
    }

    def menu_run(self, *events):
        import fep_bridge
        import windev
        psi = fep_bridge.PsiSide()
        psi.user = list(events)
        stop = psi.run(lambda out: [])
        self.assertEqual(stop.cause, 'would suspend')
        return psi.m, windev.device(psi.m).frame

    def test_win_m6_system_menu(self):
        # M6: the system menu drawn when invoked, by the mouse (OURS event
        # form {mouse, Button, X, Y} / {move, X, Y}, coordinator.esp): the
        # right button opens it with its top-left at the mouse
        # (menu_pane.esp), titled SYSTEM MENU, the HELD me:login.com's
        # items in its two columns (7 + 3); moving onto an item boxes it
        # (exclusive_or, so moving off erases the box exactly); the left
        # button on "Login PIMOS" closes the menu and starts the HELD
        # pimfep##pimos_login_requester, whose window is centred on the
        # click.  Injections: test_win_m4_console's header (J7, J8).
        import fep_bridge as FB
        import windev
        x, y = FB.MENU_AT
        move = lambda px, py: K.Vec([K.Atom('move'), px, py])   # noqa: E731
        m, fr = self.menu_run(FB.mouse('rr', x, y))
        pin_open = (windev.pbm_sha256(fr), fr.count())
        self.assertEqual(pin_open, self.MENU_PINS['open'])
        M = m.get_slot(K.ClassRef('simpos##coordinator'), 'menu_pane')
        self.assertEqual([K.resolve(m.get_slot(M, k)) for k in ('x', 'y', 'w', 'h', 'items_top')],
                         [x, y, 499, 135, 581])
        self.assertEqual(windev.read_cells(fr, x + 2, y + 3, 45, 1), [' ' * 17 + 'SYSTEM MENU'])
        cols = [['debugger', 'pmacs', 'file ', 'librarian', 'shell', 'spooler', 'pattern editor'],
                ['Pseudo Multi-PSI', 'Login PIMOS', '(Pseudo)Multi-PSI Installer']]
        cx = x + 2
        for col, w in zip(cols, (176, 319)):
            for r, label in enumerate(col):
                lx = cx + (w - 11 * len(label)) // 2
                self.assertEqual(windev.read_cells(fr, lx, 581 + 16 * r + 1, len(label), 1),
                                 [label.rstrip()], label)
            cx += w
        # boxed: the item's 1-dot rectangle, column 2 row 2
        m, fb = self.menu_run(FB.mouse('rr', x, y), move(*FB.LOGIN_ITEM_AT))
        self.assertEqual((windev.pbm_sha256(fb), fb.count()), self.MENU_PINS['boxed'])
        bx, by, bw, bh = x + 2 + 176 + 1, 581 + 16, 319 - 2, 16
        diff = [fr.rows[i] ^ fb.rows[i] for i in range(1024)]
        for yy in range(by, by + bh):
            span = ((1 << bw) - 1) if yy in (by, by + bh - 1) else (1 << (bw - 1)) | 1
            self.assertEqual(diff[yy], span << (1280 - bx - bw), yy)
        self.assertEqual(sum(bin(d).count('1') for d in diff), 2 * bw + 2 * (bh - 2))
        # moved off every item: the box erased, the frame the open menu's
        m, fo = self.menu_run(FB.mouse('rr', x, y), move(*FB.LOGIN_ITEM_AT), move(x + 10, y + 134))
        self.assertEqual((windev.pbm_sha256(fo), fo.count()), pin_open)
        # the left button on the item: the menu closed, the requester started
        m, fl = self.menu_run(FB.mouse('rr', x, y), FB.mouse('l', *FB.LOGIN_ITEM_AT))
        (p,) = self._walk(m.get_slot(K.ClassRef('simpos##coordinator'), 'started'))
        self.assertEqual(m.get_slot(K.ClassRef('simpos##coordinator'), 'menu_pane'), 0)
        top = K.deref(K.resolve(m.get_slot(m.get_slot(p, 'invocation_stack'), 'elements')).args[0])
        pane = m.get_slot(m.get_slot(top, 'window'), 'pane')
        self.assertEqual([m.get_slot(pane, k) for k in ('x', 'y')], [755, 544])
        # the menu's rectangle left of the new window is clear
        self.assertEqual(sum(bin((fl.rows[yy] >> (1280 - 755)) & ((1 << (755 - x)) - 1)).count('1')
                             for yy in range(y, y + 135)), 0)


if __name__ == '__main__':
    unittest.main()
