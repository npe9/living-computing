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
17. Nested disjunctions (2026-11-26, NestedDisjunction): `(A ; B) ; C`
   is two $or$s as in the held code (espc.py alternatives/1), and kl0
   gives a $or$ its own cut barrier (TM-388 4.6 p.111); the injections
   are in the class header.

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


_KAPPA2 = None


def kappa2():
    """(held library, espc.check('kappa2')), computed once."""
    global _KAPPA2
    if _KAPPA2 is None:
        import librarian as LB
        lib = LB.Librarian()
        lib.load_held(pkgs=espc.PROGRAMS['kappa2'])
        _KAPPA2 = lib, espc.check('kappa2', lib)
    return _KAPPA2


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
        # compile, none exact, no compared one changes its class.  1280 /
        # 258 before window M10's key macros (mouse#B, key#N, control#"c",
        # pf#N: espc.py key_constant; row by row against the macros
        # disabled, 2026-11-26): as_view_select_window read/2 (p_menu.esp)
        # and time_graph_window read_com/2 compile (refused -> moves and
        # environment), and read/2's $or$s are compared (4 other, 3 held
        # only); none exact, no compared row changes its class.  But
        # read/2 nests five deep, and the held compiler puts its three
        # X-range disjunctions one level deeper than espc does
        # (read/2.35#1#1#1#1#1-3 held, #1#1#1#3 and #1#1#2 ours): so two
        # $or$s are paired with another arity and two are compiled only,
        # the first such rows.  FOUND (2026-11-26, a compile probe): espc
        # flattens a parenthesised disjunction that is an outer one's first
        # alternative, `(A ; B) ; C`, into ONE $or$ of three clauses
        # (espc.py flat/2 in disjunction/3; the probe `((Y<1,!,fail ;
        # Y>=1,!,fail) ; R=c)` gives the single local $or$0/2), and the
        # held rows (one level deeper, three leaves under it) fit the held
        # compiler keeping the inner $or$ its own predicate.  A cut is
        # local to its $or$, so this is a BEHAVIOURAL difference, not only
        # numbering: held, `A, !, X` with X failing fails the inner $or$
        # and C is still tried; ours, the cut commits past C.
        # FIXED 2026-11-26 (espc.py alternatives/1; NestedDisjunction):
        # 1,289 compared, 258 exact.  read/2's three X-range $or$s
        # (#1#1#1#1#1-3) are compared ('other', like the rest of read/2),
        # #1#1#1#1 and #1#1#1#2 pair at the held arity 3 (2 before), the
        # two compiled-only rows are gone, and #1#1 other -> moves and
        # environment.  Both invariants are back to 0
        self.assertEqual((c['pred compared'], c['pred exact']), (1289, 258))
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


class NestedDisjunction(unittest.TestCase):
    """`(A ; B) ; C` is two $or$s, the inner one called from the outer
    one's first clause; `A ; B ; C` and `A ; (B ; C)` are one $or$ of
    three clauses (espc.py alternatives/1: a disjunction's alternatives
    are its right spine).  MEASURED on the held code: every left-nested
    disjunction in the census sources (seven: paragraph p_menu.esp
    as_view_select_window :read/2; kappa2 stwin.esp pb_status_window
    :get_number/3 and :get_font/3, kappaMDM_parse parse_occ/3, kappaCCT
    copy_table/1, two in pb_bck_cell search_enzan_code/7) has the held
    $or$ paths and arities this rule gives (search_enzan_code's only
    where espc compiles them: the predicate is refused), and read/2's
    parenthesised right argument is one $or$ (held #1#1 has arity 3, a
    separate $or$ would share 4).  utter, psi/standin, the M10 held
    members, the printed listings and the ESP in the tests have none.

    It is behavioural because a cut is local to its $or$ (PRINTED:
    TM-388 4.6 p.111, PDF p.123, Example 2, and App. G pp.161-162: in
    Prolog the cut "cuts also" the clause's alternative, in ESP it does
    not).  kl0 gives a $or$ its own barrier since 2026-11-26 (it kept
    the caller's before, so a cut in any $or$ cut the clause).  The held
    stwin.esp get_number/3 is the case: `((equal_string(N,""),!,fail ;
    :get_number(#symbolizer,Number,N)) ; Number = abort)` answers
    `abort` on an empty line only if the cut stays in the inner $or$;
    held get_number/3.35#1 is c4 / call #1#1 / c0 / get abort, and #1#1
    holds the d5 (`!, fail`) and the send.

    Injections (2026-11-26, observed; each into the working file from a
    backup copy, restored by cp, cmp clean):
    - A, espc.py alternatives/1 returning flat(t, ';') again (the
      flattening): test_shape, test_cut_scope_on_kl0 (p at Y=0 gives
      `[]`), test_held_rows, Structure.test_counts (1,286) and
      MacroBank.test_kappa2 (12,963) fail; nothing else (110 run).
    - B, kl0.py call_local not entering a kind 0x12 predicate again (a
      $or$ keeps its caller's barrier): only test_cut_scope_on_kl0 fails
      (p at Y=0 gives `[]`); test_kl0.py passes (49 tests), so nothing
      else in either file depended on the clause-wide cut.
    """
    T = '''class t has
:p(C, Y, R) :- ((Y < 1, !, fail ; Y >= 5, R = b) ; R = c);
:q(C, Y, R) :- (Y < 1, !, fail ; Y >= 5, R = b ; R = c);
end.'''

    @classmethod
    def setUpClass(cls):
        ts, failed = espc.compile_text(cls.T, 'user')
        assert not failed and not any(t.refusals for t in ts)
        (cls.t,) = ts
        cls.m = K.Machine(espc.library(ts))

    def test_shape(self):
        # p: $or$0 (two clauses, the first calling $or$1), $or$1 (two);
        # q: $or$2, three clauses
        t = self.t
        ors = {p.name: p for p in t.preds() if p is not None and p.kind == 0x12}
        self.assertEqual(sorted((n, p.arity) for n, p in ors.items()),
                         [('$or$0', 2), ('$or$1', 2), ('$or$2', 2)])
        choice = {n: [op for _tag, op, _a, _b in code(t, n) if op in (0xe4, 0xe2, 0xe0)]
                  for n in ors}
        self.assertEqual(choice, {'$or$0': [0xe4, 0xe0], '$or$1': [0xe4, 0xe0],
                                  '$or$2': [0xe4, 0xe2, 0xe0]})
        self.assertEqual(sorted(v for v in espc.canonical(t).values() if '#' in v),
                         ['p/3.25#1', 'p/3.25#1#1', 'q/3.25#1'])

    def test_cut_scope_on_kl0(self):
        # Y=0: p's cut fails only the inner $or$, so R = c is still tried;
        # q's cut is in the one $or$ and commits past R = c.  Y=3 and Y=7
        # are controls (every rule agrees)
        got = {sel: [K.call_class_method(self.m, 'user##t', sel, [y, K.Var()]) for y in (0, 3, 7)]
               for sel in ('p', 'q')}
        self.assertEqual(repr(got['p']), '[[[0, c]], [[3, c]], [[7, b], [7, c]]]')
        self.assertEqual(repr(got['q']), '[[], [[3, c]], [[7, b], [7, c]]]')

    def test_held_rows(self):
        lib, r = kappa2()
        cid = 'kappa##pb_status_window'
        rows = {x[1]: x[2] for x in r['rows'] if x[0] == cid and '#' in x[1]}
        self.assertEqual(rows, {'get_number/3.35#1 12': 'moves and environment',
                                'get_number/3.35#1#1 12': 'registers',
                                'get_font/3.35#1 12': 'moves and environment',
                                'get_font/3.35#1#1 12': 'other'})
        ht, t = lib.templates[cid], r['templates'][cid]
        ch, cn = espc.canonical(ht), espc.canonical(t)
        hs = {ch[p.offset]: p for p in ht.preds() if p is not None}
        cs = {cn[p.offset]: p for p in t.preds() if p is not None}
        for k in ('get_number/3.35#1', 'get_number/3.35#1#1', 'get_font/3.35#1'):
            self.assertEqual(hs[k].arity, cs[k].arity, k)
            self.assertEqual(espc.semantic(espc.normal(t, cs[k], espc._pool_ours, cn)),
                             espc.semantic(espc.normal(ht, hs[k], espc._pool_held, ch)), k)
        # the outer $or$ calls the inner one, then `Number = abort`
        self.assertEqual(espc.semantic(espc.normal(t, cs['get_number/3.35#1'], espc._pool_ours, cn)),
                         [('call', 'get_number/3.35#1#1'), ('const', 'abort')])
        # paragraph read/2: the three X-range $or$s, one level deeper, compared
        got = {x[1]: x[2] for x in check()['rows'] if x[0] == 'paragraph##as_view_select_window'}
        for k in ('read/2.35#1#1#1#1#1 12', 'read/2.35#1#1#1#1#2 12', 'read/2.35#1#1#1#1#3 12'):
            self.assertEqual(got[k], 'other', k)


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
        _lib, r = kappa2()
        c = r['counts']
        self.assertEqual((c['classes compiled'], c['class refused']), (739, 0))
        # with the string built-ins (step 3b): 10,641 compared, 1,361 exact
        # with the step 3c rows: 12,479 compared, 1,485 exact
        # with the step 3d rows: 12,816 compared, 1,513 exact (none lost)
        # with X*Y on two registers (blt 42, 2026-11-25): 12,871 compared,
        # 1,514 exact (with_kappaMDU_table_with_pp tab/3 newly exact; no
        # compared predicate changes its class)
        # with window M10's key macros (mouse#B, key#N, control#"c", pf#N;
        # row by row against them disabled, 2026-11-26): 12,963 compared,
        # 1,518 exact: kappaFMP_editor2 command/3, kappaFMP_kappa_file_
        # manipulator describe/3 and kappaLUU_load get_new_table_name/4
        # refused -> exact, kappaFMP_dump dumpLine/6.11#1 other -> exact;
        # none lost; 10 compared rows other -> moves and environment and
        # one other -> clause order, closer to the held cells
        # with `(A ; B) ; C` kept as two $or$s (2026-11-26,
        # NestedDisjunction; row by row against the flattening): 12,967
        # compared, 1,518 exact.  Six left-nested disjunctions: their new
        # inner $or$s are compared (get_number/3.35#1#1 registers,
        # get_font/3.35#1#1 other, parse_occ/3.35#1#1 other,
        # copy_table/1.11#2#1#1 clause order) and outer ones move closer
        # (get_number and get_font #1 other -> moves and environment,
        # copy_table/1.11#2#1 other -> clause order).  In pb_bck_cell's
        # refused search_enzan_code/7, #5#3#2#2#1#1 and #5#5#2#2#1#1 and
        # their #1s now pair at the held arity 6 (moves and environment,
        # 'other' or not compared before), while the held arity-9
        # #...#2#2#1s, paired with our flattened arity-6 $or$s before, are
        # now ours apart and refused (they call the refused
        # check_value_attribute/3), so they count as `$or$ of a refused
        # predicate`
        self.assertEqual((c['pred compared'], c['pred exact']), (12967, 1518))
        # 21 before the fix; the three gone are copy_table/1.11#2#1 (held
        # arity 2, ours 3) and the two search_enzan_code #...#2#2#1 (9,
        # 6).  The 18 left are not disjunction nesting (not examined)
        self.assertEqual(c['$or$ paired with another arity'], 18)
        # the held cells witness two of the key macros' values (espc.py
        # key_constant): KMACS2.ESP `:command(Self,mouse#r,kappa_menu)` is
        # exact only with mouse#r the atom named `mouse#r`, and DUMP.ESP
        # dumpLine/6's `Char == key#lf` only with key#lf = 10.  Injected
        # (scratch monkeypatch of key_constant, 2026-11-26): key#lf -> 11
        # loses exactly dumpLine/6.11#1 (1,517 exact); mouse#r named
        # `mouse#rx` loses exactly command/3 (1,517)
        exact = {(x[0], x[1]) for x in r['rows'] if x[2] == 'exact'}
        self.assertIn(('kappa##kappaFMP_editor2', 'command/3 35'), exact)
        self.assertIn(('kappa##kappaFMP_dump', 'dumpLine/6.11#1 12'), exact)
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
            'simpos##binary_file', 'simpos##bitmap', 'simpos##boot_process',
            'simpos##bounded_channel', 'simpos##bounded_post_queue', 'simpos##buffer_region', 'simpos##channel',
            'simpos##common_network', 'simpos##context', 'simpos##coordinator',
            'simpos##coordinator_program', 'simpos##date_time', 'simpos##directory',
            'simpos##e_string', 'simpos##editor_command_interpreter', 'simpos##editor_text_buffer',
            'simpos##font', 'simpos##hash_index', 'simpos##list', 'simpos##list_index',
            'simpos##marker',       # window M8's markers (2026-11-26)
            'simpos##menu_pane',
            'simpos##message', 'simpos##monogyny_list_index', 'simpos##name', 'simpos##network_listener_buffer',
            'simpos##network_node_name', 'simpos##network_subsystem',
            'simpos##password_list', 'simpos##pathname',
            'simpos##pmacs_display',        # window M10 (2026-11-26)
            'simpos##pmacs_request',
            'simpos##pmacs_standard_editor',        # window M10
            'simpos##pmacs_window',
            'simpos##port', 'simpos##post_queue',
            'simpos##post_queue_for_message', 'simpos##process', 'simpos##process_clock',
            'simpos##save_memory', 'simpos##semaphore',
            'simpos##standard_choice_window',       # window M9 (2026-11-26)
            'simpos##standard_editor',
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
        # window M7's rest (2026-11-26): 1,483 -> 1,485 rows, pmacs_window's
        # set_permission/2 and has_been_selected/1 inherited by
        # pimos_window, both success; no other row changes.  823 / 239 / 406
        # window M9 (2026-11-26): pimfep superviser error_mode_menu/2
        # refused -> success (its held create_error_mode_menu/1 reaches
        # the new standard_choice_window stand-in; before, the class was
        # missing); rows unchanged.  824 / 239 / 405
        # window M10 (row by row against f825683e's stand-ins, 2026-11-26):
        # 1,485 -> 1,520 rows (1,521 below), all 35 new rows inherited from stand-ins, no
        # row removed, no held row changes outcome.  pimos_window gets 8 of
        # pmacs_window's new methods: clear_echo_area/1, echo/2, kill/1
        # success; current_buffer/2, menu_chosen/2, refresh/1,
        # right_click/3, set_input_buffer/2 refused at the census window's
        # unset interpreter (slot constant).  pimos_window_editor gets 27 of
        # standard_editor's: abort/1, control_x/3, exit/1, save_all_files/1,
        # show_menu/1 success; read_file/4 refused (unbound pathname); the
        # other 21 refused at the census editor's unset window (slot
        # constant).  The held select_buffer/4 moves its stop from
        # editor_text_buffer get_buffer_instance/3 (now stood in) to
        # set_input_buffer/2 on that unset window.  832 / 239 / 432.
        # Then set_input_position/1 (cal_pmacs run/4) inherited by
        # pimos_window, success: 1,521 rows, 833 / 239 / 432
        self.assertEqual((len(rows), out), (1521, {'success': 833, 'failure': 239, 'refused': 432, 'exception': 16,
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
        # editor slot) stop at the census's slot constants; 158 -> 185 in
        # window M10: the 26 new rows above and select_buffer/4
        self.assertEqual(sum(1 for r in rows if r[4] == 'receiver a slot constant'), 185)
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
        # window M7's rest: + set_permission/2, has_been_selected/1 in
        # pimos_window (success), as in test_fep_census.  Window M9:
        # error_mode_menu/2 refused -> success, as there.  855 / 241 / 372
        # window M10 (row by row against f825683e's stand-ins): the 35 new
        # rows of test_fep_census, here (recipes: a window with an
        # interpreter, an editor with a window) 25 success, 9 failure
        # (backward_character/1, delete_backward_character/1,
        # delete_character/1, forward_character/1, insert/2, kill_line/1,
        # next_line/1, previous_line/1, select_buffer/1: the census
        # window's empty buffer has no character to move over or delete and
        # no other line, insert/2's unbound argument is not inserted, and
        # no buffer is in the pool to select) and
        # read_file/4 refused (unbound pathname); select_buffer/4 moves its
        # stop from get_buffer_instance/3 to put/2 on the window's unset
        # output stream (the step 3g artifact).  No held row changes
        # outcome.  880 / 250 / 373; set_input_position/1 (as in
        # test_fep_census) success: 1,521 rows, 881 / 250 / 373
        self.assertEqual((len(rows), out), (1521, {'success': 881, 'failure': 250, 'refused': 373,
                                                   'exception': 16, 'step limit': 1}))
        slot_const = sum(1 for r in rows if r[4] == 'receiver a slot constant')
        # step 3l: 107 -> 110, as in test_fep_census; step 3n: 111, get_title/3;
        # window M0: 111 -> 108 (the login requester's three rows, as in
        # test_fep_census); window M4: 108 -> 114, the editor's
        # buffer_name/3, clear/3, reshape/7, reshape_by_mouse/3,
        # set_inside_size/5, set_size/3 go from 'simpos' (an unstood
        # pmacs_window or editor method) to put/2 on the window's unset
        # output stream (the step 3g artifact, as get_title/3); window M10:
        # 114 -> 115, select_buffer/4 (above)
        self.assertEqual(slot_const, 115)
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
            self.assertEqual(len(fwd), 1521)    # window M10: 36 inherited methods (test_fep_census)
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
    # and its box naming standard_io_window/1; then the band's date, 941
    # dots fewer, M6_PINS before it: see DATE)
    PINS = {
        'name': ('20f7c567fdf7728f202f99ee70e1b67636ae3fb8e3e8fa3602d87c92958eec54', 102011),
        'password': ('d2a2021d034858a4616549858ff6f459d7bd8792b04b61ad4b2584cafe99d69b', 103080),
        'login': ('5c90d0d7d4e07834243e28e3684b69442aa45b14f7e4d1e109de75c5506b62af', 102774),
    }
    M6_PINS = {
        'name': ('4a31e4ae4ffddcfd377679180525b2cfdcc07cd08f3d666d23bb05ef212d30bb', 102952),
        'password': ('28728b793499409abe820be92455041b85d1bbee03360f5273d3a4ce3645be43', 104021),
        'login': ('c1afaf8cd4050773b32f47d874bc700faa7d34f0caa5487978f66cd024287b17', 103715),
    }

    # window M6, the date (status_band.esp): drawn white on black at the
    # right of the band's second row, from the PSI's date_time (day 33742,
    # time 0: date_time.esp).  Every frame with the band has 941 dots
    # fewer than before it (the 27 cells' glyphs inverted), and with the
    # date's rectangle set black again it equals its pin from before the
    # date (the M6_ pins): the date is all that changed.
    DATE = '20-May-93 Thursday 00:00:00'
    DATE_AT = (975, 974, 27 * 11, 14)

    def assert_date(self, fr, before):
        import windev
        import winfb
        x, y, w, h = self.DATE_AT
        g = winfb.Frame()
        g.rows = [r ^ ((1 << 1280) - 1) for r in fr.rows]
        self.assertEqual(windev.read_cells(g, x, y, 27, 1), [self.DATE])
        g.rows = list(fr.rows)
        g.command(winfb.FILL << 4 | 0, [x, y, w, h, 0, 0])
        self.assertEqual((windev.pbm_sha256(g), g.count()), before)
        self.assertEqual(fr.count(), before[1] - 941)
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
        # Window M6's date (2026-11-25): every stage's pin moved by -941
        # dots (PINS; M6_PINS before the date), accounted by assert_date
        # (DATE): with the date's rectangle set black again the frame is
        # its M6 pin.
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
                self.assert_date(fr, self.M6_PINS.get(stage))
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
    # M5_BRIDGED_PIN, which the frame with the band cleared still equals;
    # then the date (DATE): 941 fewer, M6_BRIDGED_PIN before it
    BRIDGED_PIN = ('7ffdf41ae544a47a6b77a087cb8b13c6d09b7d0c6a2e18328ba898b3f3ee53a1', 102783)
    M6_BRIDGED_PIN = ('c33da8f127897aea8501f68ae999bcc33dda26df6ec890281b2e29c11007d614', 103724)
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
        self.assert_date(fr, self.M6_BRIDGED_PIN)
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
                          ('system_menu', self.MENU_PINS['boxed']),
                          ('menu_over_window', self.SHOT_PINS['over']),
                          ('create_kill_popup', self.SHOT_PINS['popup']),
                          ('rubber_band', self.SHOT_PINS['sweep']),
                          ('window_manipulator', self.SHOT_PINS['manip']),
                          ('manipulator_hide', self.SHOT_PINS['hidden']),
                          ('manipulator_reshape', self.SHOT_PINS['reshaped']),
                          ('manipulator_expand', self.SHOT_PINS['expand']),
                          ('manipulator_menu', self.SHOT_PINS['windows']),
                          ('notify_window', self.SHOT_PINS['notify']),
                          ('window_graphics', self.GRAPHICS_PIN),
                          ('window_graphics_rest', self.GRAPHICS_REST_PIN),
                          ('choice_window', self.CHOICE_PIN),
                          ('manipulator_attribute', self.SHOT_PINS['attribute']),
                          ('pmacs_editor', self.M10_PINS['pmacs']),
                          ('editor_menu', self.M10_PINS['editor_menu'])):
            with open(os.path.join(shots, '%s.png' % name), 'rb') as f:
                g = winfb.Frame()
                g.rows = windev.png_rows(f.read())
            self.assertEqual((windev.pbm_sha256(g), g.count()), pin, name)

    # the M4 run's final screen; M6_CONSOLE_PIN before the date (DATE),
    # which the tape's recorded screen is (recorded before the date)
    CONSOLE_PIN = ('b3e0ea5030adfae107f0867d90257e573c8acf90c1a8cf313715f8d7bb692b46', 109735)
    M6_CONSOLE_PIN = ('f9da0fe2881c5bd15fd41c07608396991eec0775a6295faa485f205e602b4a53', 110676)

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
        # Window M6's date (2026-11-25): this run's frame has 941 dots
        # fewer than CONSOLE_PIN had before it (now M6_CONSOLE_PIN), the
        # band's date; assert_date and DATE account for it.
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
        self.assert_date(fr, self.M6_CONSOLE_PIN)
        # the tape's result was recorded before the band's date: it is the
        # frame with the date's rectangle black again
        self.assertEqual(t['result']['screen'], dict(sha256=self.M6_CONSOLE_PIN[0], dots=self.M6_CONSOLE_PIN[1]))
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
        'open': ('023384cbc9c34fda9121814c18cd4647289ffa52f29c3f31e2a11d673b44939d', 107420),
        'boxed': ('708b7cff434691f178291e17644fbdc3a4c5822673d88d065743d5c8f0a30474', 108082),
    }
    # before the band's date (DATE)
    M6_MENU_PINS = {
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
        self.assert_date(fr, self.M6_MENU_PINS['open'])
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
        self.assert_date(fb, self.M6_MENU_PINS['boxed'])
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


    def test_standin_refusals_loud(self):
        # espc's refusals in a stand-in fail loud (espc.standins,
        # check_standin_refusals, 2026-11-25): only the listed HELD-SOURCE
        # bodies of KNOWN_STANDIN_REFUSALS are refused, every entry of the
        # list is still refused (none stale), and a new refusal, here
        # date_time's first get_value/8 (`/ 3600000`: no witnessed
        # immediate above 255), is a CompileRefusal naming the predicate.
        # Injection, OBSERVED (2026-11-25, from a backup copy, restored by
        # copy, cmp clean): E1 check_standin_refusals a no-op: this test
        # FAILS, nothing else in this file or test_kl0.py.
        refused = {(t.id, k[0], k[1]) for t in self.ts for k, _w, _d in t.refusals}
        self.assertEqual(refused, espc.KNOWN_STANDIN_REFUSALS)
        text = """class probe_clock has
:hour(Class, T, H) :- value(T / 3600000, H);
local
value(V, V);
end.
"""
        ts, failed = espc.compile_text(text, 'simpos')
        self.assertFalse(failed)
        with self.assertRaises(espc.CompileRefusal) as e:
            espc.check_standin_refusals(ts, 'probe_clock.esp')
        self.assertIn('simpos##probe_clock refuses hour/3: arithmetic immediate', str(e.exception))

    def test_espc_swallowed_head(self):
        # espc fails loud on a clause whose head was swallowed by the
        # comment line before it (espc.compile_text: source_refusals,
        # swallowed_heads; 2026-11-25).  Until then the body compiled with
        # no complaint: in the method part as a local clause outside the
        # local part, dropped by the parser (`unparsed`, never reported);
        # in the local part as a clause headed by ','/2, or, for a body of
        # one goal, as a fact.  Each of the four forms below is now a
        # CompileRefusal; the stand-ins and every test program still
        # compile (standins() in setUpClass).  Injections, OBSERVED
        # (2026-11-25, from a backup copy, restored by copy, cmp clean):
        #   E2 source_refusals answers [] and swallowed_heads [] (the old
        #      behaviour): this test FAILS, nothing else in this file,
        #      test_kl0.py or test_fep_bridge.py.
        #   E3 swallowed_heads alone answers []: this test FAILS (the
        #      one-goal body in the local part, which only the source text
        #      shows), nothing else.
        def compiled(part, body):
            if part == 'local':
                text = "class t has\n:ok(C) :- true;\nlocal\n%s\nbar(_);\nbaz(_);\nend.\n" % body
            else:
                text = "class t has\n:ok(C) :- true;\n%s\nlocal\nbar(_);\nbaz(_);\nend.\n" % body
            return espc.compile_text(text, 'user')
        for part, body, why in (
                ('method', '% the head  :foo(C, X) :-\n        bar(X), baz(X);', 'outside the local part'),
                ('method', '% the head  :foo(C, X) :- !,\n        bar(X);', 'outside the local part'),
                ('local', '% the head  foo(X) :-\n        bar(X), baz(X);', 'a clause headed by ,/2'),
                ('local', '% the head  foo(X) :-\n        bar(X);', 'a comment ending as a clause head')):
            with self.assertRaises(espc.CompileRefusal, msg=body) as e:
                compiled(part, body)
            self.assertEqual(e.exception.construct, 'source')
            self.assertIn(why, str(e.exception))
        # the same with the head on its own line compiles
        ts, failed = compiled('local', '% the head\nfoo(X) :-\n        bar(X), baz(X);')
        self.assertFalse(failed)
        self.assertIn(('foo', 1), [(p.name, p.arity) for p in ts[0].preds() if p is not None])

    def test_win_m6_date(self):
        # M6, the band's date source: date_time get_value/8 and set_count/3
        # (INTERPOLATED from cil/src/ms_ist.esp:735-742, HELD-SOURCE; the
        # calendar OURS, day 0 = 01-Jan-1901 as PIMOS counts) against
        # Python's calendar, across 1901, the banner day 33742 (fep.py
        # DATE, the PSI's default), the leap day of 2000 and the end of a
        # day; the band's weekday (status_band.esp) is pinned through DATE
        # in every band pin.  Injections, OBSERVED (2026-11-25, re-run at
        # the final commit; from a backup copy, restored by copy, cmp
        # clean; Window, test_fep_bridge.py and test_kl0.py run, all else
        # OK):
        #   D1 the calendar counted from 1900: this test, the three M5
        #      stages, the bridged screen, M4, the system menu,
        #      test_win_m7_save_areas and test_win_m6_create_kill FAIL.
        #   D2 the weekday off by one ((N + 3) mod 7): the same set
        #      without this test (it does not read the weekday).
        import datetime
        sys.path.insert(0, os.path.join(HERE, '..', 'ref', 'pimm'))
        import fep
        m = self.fs_machine()
        self.assertEqual([m.get_slot(K.ClassRef('simpos##date_time'), k) for k in ('date', 'time')],
                         [fep.DATE, 0])
        for d, t in ((0, 0), (33742, 0), (33742, 45296789), (36218, 1), (36524, 86399999),
                     (36583, 1), (40000, 0)):
            m.reset()
            ((D,),) = K.call_class_method(m, 'simpos##date_time', 'create', [K.Var()])
            m.reset()
            self.assertTrue(any(True for _ in m.solve_send(D, 'set_count', [d, t, D])))
            m.reset()
            regs = [K.Var() for _ in range(7)]
            self.assertTrue(any(True for _ in m.solve_send(D, 'get_value', regs + [D])))
            got = [K.resolve(v) for v in regs]
            dd = datetime.datetime(1901, 1, 1) + datetime.timedelta(days=d, milliseconds=t)
            self.assertEqual(got, [dd.year, dd.month, dd.day, dd.hour, dd.minute, dd.second,
                                   dd.microsecond // 1000], (d, t))
        self.assertEqual((datetime.date(1901, 1, 1) + datetime.timedelta(fep.DATE)).strftime('%d-%b-%y %A'),
                         self.DATE[:18])

    def later_run(self, first, *then):
        # window M6/M7: FIRST given at the first quiet moment (as
        # menu_run), each batch of THEN at the next one, after the
        # processes the batch before started have drawn (fep_bridge's
        # shell batch, its getl condition set, refilled from THEN).  ->
        # (machine, frame, the refusal that ended the run)
        import fep_bridge
        import windev
        psi = fep_bridge.PsiSide()
        psi.user, rest = list(first), [list(b) for b in then]

        def exchange(out):
            if rest and not psi.shell:
                psi.shell, psi.getl = rest.pop(0), True
            return []
        stop = psi.run(exchange)
        self.assertEqual((rest, psi.shell), ([], []))
        return psi.m, windev.device(psi.m).frame, stop

    # window M6/M7 screens (psi/winshot.py): the event batches (later_run)
    # and the frames' pins
    @staticmethod
    def shot_events():
        import fep_bridge as FB
        L = FB.mouse
        login = [L('rr', *FB.MENU_AT), L('l', *FB.LOGIN_ITEM_AT)]
        pop = [L('rr', 200, 150), L('l', 500, 195)]
        return dict(
            over=lambda: (login, [L('rr', 700, 500)]),
            popup=lambda: (login, pop),
            sweep=lambda: (login, pop + [L('l', 540, 220), L('l', 600, 500),
                                         K.Vec([K.Atom('move'), 900, 600])]),
            # window M7 (test_win_m7_manip): the manipulator open over
            # window 2; window 2 hidden under window 1; window 2 reshaped
            manip=lambda: (login, Window.manip_events()['two'], Window.manip_events()['menu']),
            hidden=lambda: (login, Window.manip_events()['two'], Window.manip_events()['hide']),
            reshaped=lambda: (login, Window.manip_events()['two'], Window.manip_events()['reshape']),
            # window M7's other items and permissions (test_win_m7_items,
            # test_win_m7_permissions): EXPAND; MENU's submenu; the
            # notify window of window 2, covered as it writes
            expand=lambda: (login, Window.manip_events()['two'], Window.manip_events()['move'],
                            Window.manip_events()['expand']),
            windows=lambda: (login, Window.manip_events()['two'], Window.manip_events()['windows']),
            notify=lambda: (login, Window.manip_events()['two'], Window.permission('notify'),
                            Window.manip_events()['late']),
            # window M9 (test_win_m9_attribute): the manipulator's
            # ATTRIBUTE sheet open on window 2
            attribute=lambda: (login, Window.manip_events()['two'], Window.manip_events()['attribute']))

    # PERMISSION's submenu items (manip_events' `permission`), for window 2
    @staticmethod
    def permission(name):
        import fep_bridge as FB
        i = ('out', 'wait', 'show', 'notify').index(name)
        return Window.manip_events()['permission'] + [FB.mouse('l', 760, 705 + 7 + 16 * i)]

    SHOT_PINS = {
        'over': ('a398542a5a3d589728d533c59c9b01ce551f2a487e839b2a7e15bb2220c599b3', 104904),
        'popup': ('42bfaa7dd1c4e7d2fc1c703be0569243e5cfc96cf639edd3081db31832c26058', 102627),
        'sweep': ('d329f4fbb05d319a26922c63e309efdc7313863c96e978b88ecddfea82d2b6a9', 101796),
        # window M7, the manipulator (test_win_m7_manip)
        # (window M9: nine items, ATTRIBUTE added; was e7201fee..., 106,491)
        'manip': ('ff9467b90860916c1fa447c7c9a7163a70d611e2476ffd32228212064aa3c074', 106916),
        'hidden': ('4501d0323c4d5dcd0fbb9e66972aea3c0072c7e282a1e0e3d41c5eb118cedcd9', 104313),
        'reshaped': ('01b2c46048cf3292391a76cb071dce2b527c0daec656a96eab736ecdaeb0c42b', 105062),
        # window M7's other items and the notify window
        'expand': ('1e84d97537038def372a351fd19b69de090fcbfdf32403058e42daa3cda632f1', 110862),
        'windows': ('271d1a6f63b3952dfd10746b6bffc9dd425b8143c09cc3716031933fe0173d2a', 105702),
        'notify': ('ac6f26d394a276c57554e9281d85eca391f45f59a7385ae39a737fc5cf9cafcb', 106513),
        # window M9, the manipulator's ATTRIBUTE sheet (test_win_m9_attribute)
        'attribute': ('c0dcc0832e2713c91e461067b401756ea5b0a9dce6af38b701b438827d53f752', 106884),
    }

    def test_win_m6_create_kill(self):
        # M6, create and kill from the system menu (coordinator.esp head:
        # SCREENSHOT simpos.wmv@49-60, prolog.wmv@14-15, the sequence
        # INFERENCE; the sweep by two corners as TM-125 p8's RESHAPE,
        # PRINTED-INTERFACE).  With a Login PIMOS window shown, choosing
        # the item again opens a pop-up titled `Login PIMOS` with `create`
        # and `kill` at the mouse; `create`, a corner, a move: the outline
        # is exactly a 1-dot rectangle (exclusive_or) between the corner
        # and the mouse; the other corner: the outline erased and a second
        # held requester started, its window at the outline's top-left;
        # then `kill` on the same item: the newest requester is
        # exterminated and its window restores what it covered (the first
        # window), exactly.  Injections, OBSERVED (2026-11-25; each from a
        # backup copy, restored by copy, cmp clean; Window,
        # test_fep_bridge.py and test_kl0.py run, all else OK):
        #   R1 the outline's top edge drawn by set, not exclusive_or: this
        #      test FAILS, nothing else.
        #   R2 coordinator running/4 never finds a shown program (the item
        #      always starts it, no pop-up): this test ERRORS, nothing
        #      else.
        #   R3 window_pane ignores the swept placement (the window centred
        #      on the mouse): this test FAILS, nothing else.
        #   R4 coordinator cursor_aside/1 a no-op: this test FAILS,
        #      nothing else.
        # Found wrong by a probe then, fixed and pinned in window M7: keys
        # typed after `create` went first to the older requester
        # (test_win_m7_keyboard_focus); a kill under a newer window put
        # stale dots over it (test_win_m7_manip).  This test's pins did
        # not move.
        import fep_bridge as FB
        import windev
        import winfb
        L = FB.mouse
        mv = lambda px, py: K.Vec([K.Atom('move'), px, py])   # noqa: E731
        C = K.ClassRef('simpos##coordinator')
        x, y = FB.MENU_AT
        login = [L('rr', x, y), L('l', *FB.LOGIN_ITEM_AT)]
        m, before, _ = self.later_run(login)
        # the pop-up: the system menu at (200, 150), Login PIMOS (column 2,
        # row 2) at (500, 195)
        pop = [L('rr', 200, 150), L('l', 500, 195)]
        m, fp, stop = self.later_run(login, pop)
        self.assertEqual(stop.cause, 'would suspend')
        P = m.get_slot(C, 'menu_pane')
        self.assertEqual([K.resolve(m.get_slot(P, k)) for k in ('x', 'y', 'w', 'h', 'items_top')],
                         [500, 195, 147, 55, 216])
        self.assertEqual(windev.read_cells(fp, 502, 198, 13, 1), [' Login PIMOS'])
        self.assertEqual(windev.read_cells(fp, 502 + 38, 217, 6, 1), ['create'])
        self.assertEqual(windev.read_cells(fp, 502 + 49, 233, 4, 1), ['kill'])
        self.assertEqual(K.resolve(m.get_slot(C, 'dialogue')).args[0], K.Atom('which'))
        self.assertEqual((windev.pbm_sha256(fp), fp.count()), self.SHOT_PINS['popup'])
        # create, the first corner, a move: the outline only
        corner = pop + [L('l', 540, 220), L('l', 600, 500)]
        m, f1, _ = self.later_run(login, corner)
        m, f2, _ = self.later_run(login, corner + [mv(900, 600)])
        self.assertEqual(f1.rows, before.rows)
        bw, bh = 301, 101
        for yy in range(500, 601):
            span = ((1 << bw) - 1) if yy in (500, 600) else (1 << (bw - 1)) | 1
            self.assertEqual(f1.rows[yy] ^ f2.rows[yy], span << (1280 - 600 - bw), yy)
        self.assertEqual(sum(bin(a ^ b).count('1') for a, b in zip(f1.rows, f2.rows)), 2 * bw + 2 * (bh - 2))
        self.assertEqual((windev.pbm_sha256(f2), f2.count()), self.SHOT_PINS['sweep'])
        # the other corner: the outline gone, the second window at (600,
        # 500), the same frame as with no move at all
        done = corner + [mv(900, 600), mv(1100, 700), L('l', 1000, 640)]
        m, fd, stop = self.later_run(login, done)
        self.assertEqual(stop.cause, 'would suspend')
        m0, fd0, _ = self.later_run(login, corner + [L('l', 1000, 640)])
        self.assertEqual(fd.rows, fd0.rows)
        ws = self._walk(m.get_slot(C, 'windows'))
        self.assertEqual(len(ws), 2)
        pane = m.get_slot(ws[0], 'pane')
        self.assertEqual([m.get_slot(pane, k) for k in ('x', 'y', 'w', 'h')], [600, 500, 446, 121])
        self.assertEqual(windev.read_cells(fd, 603, 503, 40, 1), ['Pimos remote login 6'])
        self.assertEqual(windev.read_cells(fd, 603, 520, 40, 2), ['Enter FEP node name--------->', '#'])
        self.assertEqual(self.band(fd)[2], ['standard_io_window/2'])
        self.assertEqual(m.get_slot(C, 'placement'), K.NIL)
        # kill: the newest requester dead, its window gone, the first
        # window's dots back (its cursor taken off when the second was
        # drawn, coordinator cursor_aside/1; the band's box cleared)
        kill = [L('rr', 100, 100), L('l', 400, 145), L('l', 440, 188)]
        m, fk, stop = self.later_run(login, done, kill)
        self.assertEqual(stop.cause, 'would suspend')
        (w1,) = self._walk(m.get_slot(C, 'windows'))
        self.assertEqual([m.get_slot(m.get_slot(w1, 'pane'), k) for k in ('x', 'y')], [755, 544])
        p2 = self._walk(m.get_slot(C, 'started'))[0]
        self.assertEqual(m.get_slot(p2, 'status'), K.Atom('nil'))
        self.assertEqual(m.get_slot(C, 'selected'), 0)
        want = winfb.Frame()
        want.rows = list(before.rows)
        want.command(winfb.FILL << 4 | 2, [758, 578, 11, 14, 0, 0])      # the cursor off
        want.command(winfb.FILL << 4 | 0, [400, 950, 440, 18, 0, 0])     # the box cleared
        self.assertEqual(fk.rows, want.rows)
        self.assertEqual(len(self._walk(m.get_slot(K.ClassRef('simpos##save_memory'), 'used'))), 1)
        self.assertEqual(set(fk.status) | set(fd.status), {winfb.OK})

    @staticmethod
    def saves(m):
        import windev
        import winfb
        return [winfb.mnemonic(op, a) for op, a in windev.device(m).log
                if op >> 4 in (winfb.SAVE, winfb.RESTORE)]

    def test_win_m7_save_areas(self):
        # M7, save areas (save_memory.esp, OURS allocation; TM-225 p10 and
        # TM-126 p5 PROSE, window.md §4.1): a pop-up saves the dots under
        # it before it is drawn and restores them when it closes, through
        # winfb's save/restore (simpos##bitmap_display save/7, restore/3,
        # psi/windev.py; bsv/WinFbBox.bsv runs both in lockstep).  The
        # SYSTEM MENU is opened OVER the Login PIMOS window (its border,
        # label, prompt and the selected window's block cursor), so a
        # clear would not give back the frame.  The frame after open +
        # close equals the frame before the open, closed four ways: a click
        # off the items, with an item boxed first, a menu clamped at the
        # right edge, and a click on an item (librarian: its class is not
        # loaded, so the start refuses loudly, after the restore).  The
        # window's own area stays in use; out of save memory is a loud
        # refusal (winfb BADSAVE), never a silent clear.
        # Injections, OBSERVED (2026-11-25, re-run at the final commit
        # with every window test in place; each from a backup copy,
        # restored by copy, cmp clean; Window, test_fep_bridge.py and
        # test_kl0.py run, all else OK):
        #   S1 menu_pane erase/1 clears its rectangle (fill reset, M6's
        #      way) instead of restoring: this test and
        #      test_win_m6_create_kill FAIL.
        #   S2 save_memory always gives slot 0 (a later save replaces an
        #      earlier one's entry): this test, test_win_m6_selection and
        #      test_win_m6_create_kill FAIL.
        #   S3 save_memory restores by exclusive_or, not copy: this test,
        #      test_win_pane, the three M5 stages, the bridged screen, M4,
        #      the system menu and test_win_m6_create_kill FAIL.
        import fep_bridge as FB
        import windev
        x, y = FB.MENU_AT
        login = [FB.mouse('rr', x, y), FB.mouse('l', *FB.LOGIN_ITEM_AT)]
        m, before, stop = self.later_run(login)
        self.assertEqual(stop.cause, 'would suspend')
        self.assertEqual(self.saves(m), ['save 0 640 560 499 135 0', 'restore 0 copy',
                                         'save 0 755 544 446 121 0'])
        self.assertEqual(windev.read_cells(before, 758, 564, 40, 2),
                         ['Enter FEP node name--------->', '#'])
        # the menu at (700, 500) covers the window's left part: what is
        # under it is not blank (border, label, prompt, cursor)
        under = sum(bin((before.rows[j] >> (1280 - 700 - 499)) & ((1 << 499) - 1)).count('1')
                    for j in range(500, 635))
        self.assertEqual(under, 3005)
        m, opened, stop = self.later_run(login, [FB.mouse('rr', 700, 500)])
        self.assertEqual(self.saves(m)[3:], ['save 1 700 500 499 135 3388'])
        self.assertNotEqual(opened.rows, before.rows)
        self.assertEqual((windev.pbm_sha256(opened), opened.count()), self.SHOT_PINS['over'])
        move = lambda px, py: K.Vec([K.Atom('move'), px, py])   # noqa: E731
        for name, then, at in (
                ('off the items', [FB.mouse('l', 705, 505)], (700, 500)),
                ('boxed, then outside', [move(720, 525), FB.mouse('l', 1100, 900)], (700, 500)),
                ('clamped', [FB.mouse('l', 1100, 900)], (781, 520))):
            # the right button at (1100, 520) for the clamped menu
            m, closed, stop = self.later_run(login, [FB.mouse('rr', 1100 if name == 'clamped' else at[0], at[1])]
                                             + then)
            self.assertEqual(stop.cause, 'would suspend', name)
            self.assertEqual(self.saves(m)[3:], ['save 1 %d %d 499 135 3388' % at, 'restore 1 copy'], name)
            self.assertEqual(closed.rows, before.rows, name)
            self.assertEqual(len(self._walk(m.get_slot(K.ClassRef('simpos##save_memory'), 'used'))),
                             1, name)
        m, closed, stop = self.later_run(login, [FB.mouse('rr', 700, 500), FB.mouse('l', 720, 584)])
        self.assertEqual((stop.cause, stop.detail),
                         ('simpos', 'library get_class_object/3: simpos##librarian is not loaded'))
        self.assertEqual(closed.rows, before.rows)
        # out of save memory: loud.  A full-screen area is 80 x 944 =
        # 75,520 words > 65,536 (BADSAVE); so is a seventeenth area
        m = self.fs_machine()
        with self.assertRaises(K.Refusal) as e:
            K.call_class_method(m, 'simpos##save_memory', 'save', [0, 0, 1280, 944, K.Var()])
        self.assertEqual(e.exception.detail, 'bitmap_display save/7: winfb status 4')
        m = self.fs_machine()
        for i in range(16):
            K.call_class_method(m, 'simpos##save_memory', 'save', [0, 0, 16, 1, K.Var()])
        with self.assertRaises(K.Refusal) as e:
            K.call_class_method(m, 'simpos##save_memory', 'save', [0, 0, 16, 1, K.Var()])
        self.assertEqual(e.exception.detail, 'bitmap_display save/7: winfb status 4')
        # the refused command is logged (and refused again on a replay)
        self.assertEqual(self.saves(m)[-2:], ['save 15 0 0 16 1 15', 'save 16 0 0 16 1 16'])

    # window M7, the manipulator and keyboard focus (coordinator.esp "THE
    # STACK", "THE MANIPULATOR"; standard_io_window.esp "Window M7"): the
    # event batches (later_run) of test_win_m7_manip,
    # test_win_m7_keyboard_focus and psi/winshot.py.  Window 1 is the Login
    # PIMOS window at (755, 544); window 2, a second requester made by
    # create/kill's `create` at (600, 500), covers its top-left corner.
    # The middle button at (620, 560), on window 2, opens the manipulator
    # there: SHOW, HIDE, RESHAPE, MOVE, items 16 dots apart from y 581.
    @staticmethod
    def manip_events():
        import fep_bridge as FB
        L = FB.mouse
        mv = lambda px, py: K.Vec([K.Atom('move'), px, py])   # noqa: E731
        item = lambda i: L('l', 700, 588 + 16 * i)             # noqa: E731
        menu = L('m', 620, 560)
        return dict(
            login=[L('rr', *FB.MENU_AT), L('l', *FB.LOGIN_ITEM_AT)],
            two=[L('rr', 200, 150), L('l', 500, 195), L('l', 540, 220), L('l', 600, 500),
                 L('l', 1000, 640)],
            menu=[menu],
            hide=[menu, item(1)],
            show=[menu, item(0)],
            move=[menu, item(3), mv(300, 300), L('l', 100, 100)],
            # MOVE of the covered window 1: the manipulator opened on its
            # uncovered part (clamped at the right edge, at x 1056), MOVE
            move1=[L('m', 1100, 600), L('l', 1180, 676), L('l', 100, 100)],
            reshape=[menu, item(2), L('l', 100, 100), mv(300, 250), L('l', 500, 300)],
            reshape_band=[menu, item(2), L('l', 100, 100), mv(300, 250)],
            # window M7's other items: EXPAND of window 2 after its MOVE
            # to (100, 100) (the manipulator at (200, 150)); MENU's
            # submenu; EXIT
            expand=[L('m', 200, 150), L('l', 280, 171 + 7 + 16 * 4)],
            windows=[menu, item(5)],
            exit=[menu, item(8)],        # window M9: ATTRIBUTE is item 7
            # PERMISSION's submenu at (700, 684): out, wait, show, notify
            permission=[menu, item(6)],
            # window M9: ATTRIBUTE's sheet at (700, 700) (inside (703, 720),
            # cells 11 x 14): PERMISSION's `wait` (row 1, column 16),
            # do_it (row 2, column 2), abort (row 2, column 10)
            attribute=[menu, item(7)],
            attribute_wait=[L('l', 703 + 16 * 11 + 5, 720 + 14 + 7)],
            attribute_do_it=[L('l', 703 + 2 * 11 + 5, 720 + 28 + 7)],
            attribute_abort=[L('l', 703 + 10 * 11 + 5, 720 + 28 + 7)],
            # window 1 raised by a click while window 2 echoes `local`
            late=Standins.keys('local') + [L('l', 1100, 600)],
            # create/kill's `kill`: the newest requester (window 2)
            kill=[L('rr', 100, 100), L('l', 400, 145), L('l', 440, 188)],
            # window 2 made at (100, 100) by create/kill's sweep
            two_at_100=[L('rr', 200, 150), L('l', 500, 195), L('l', 540, 220), L('l', 100, 100),
                        L('l', 500, 300)])

    @staticmethod
    def paste(dst, src, x, y, w, h, dx=None, dy=None):
        # the W x H dots of frame SRC at (X, Y) put into DST at (DX, DY)
        dx, dy = (x if dx is None else dx), (y if dy is None else dy)
        mask = (1 << w) - 1
        for j in range(h):
            bits = (src.rows[y + j] >> (1280 - x - w)) & mask
            row = dst.rows[dy + j] & ~(mask << (1280 - dx - w))
            dst.rows[dy + j] = row | (bits << (1280 - dx - w))

    def manip_check(self, m, fr, windows):
        # after a restack save memory holds each window's own area and
        # nothing else, every device command is OK, and the stream replays
        # to the same frame.  -> the windows, top first
        import windev
        import winfb
        C = K.ClassRef('simpos##coordinator')
        ws = self._walk(m.get_slot(C, 'windows'))
        self.assertEqual([[m.get_slot(m.get_slot(w, 'pane'), k) for k in ('x', 'y', 'w', 'h')] for w in ws],
                         windows)
        self.assertEqual(len(self._walk(m.get_slot(K.ClassRef('simpos##save_memory'), 'used'))), len(ws))
        self.assertEqual(set(fr.status), {winfb.OK})
        self.assertEqual(winfb.run_stream(windev.device(m).stream_text()).pbm(), fr.pbm())
        return ws

    MANIP_W1 = [755, 544, 446, 121]
    MANIP_W2 = [600, 500, 446, 121]
    BOX_AT = (400, 950, 440, 18)

    def test_win_m7_keyboard_focus(self):
        # M7, keyboard focus (standard_io_window.esp, coordinator.esp):
        # each window reads its own input stream, and the coordinator puts
        # a key on the selected window's (typed/2).  Basis: the selected
        # window has the keyboard (PROSE TM-225 p11, TM-115 p111;
        # window.md §2.7, §4.1); a window is selected by showing it
        # (TM-225 p10-11) or by a left click on it (PRINTED TR-046 p28
        # `mouse#l` visit; PROSE TM-115 p111), which also brings it to the
        # top (INFERENCE, TM-225 p11: the selected window is the top of
        # the stack).  Until M7 every requester read the coordinator's one
        # keyboard stream, so after `create` the first key of `local` went
        # to the older requester, already waiting in get/2 (README "Open").
        # Keys typed while no window is selected go to the next one
        # selected (coordinator type_ahead/2, OURS).
        # Injections, OBSERVED: see test_win_m7_manip's header (F1b, F1,
        # F3, M1 and M6 fail this test; F2 fails the earlier ones).
        import fep_bridge as FB
        import windev
        E = self.manip_events()
        C = K.ClassRef('simpos##coordinator')

        def history(m, w):
            return [h if isinstance(h, int) else h.text for h in reversed(self._walk(m.get_slot(w, 'history')))]
        local = K.Str('local').codes() + [13]
        prompt = ['Enter FEP node name--------->']
        then = prompt + local + ['Enter your PIMOS user name-->']
        m, fr, stop = self.later_run(E['login'], E['two'], self.keys('local'))
        self.assertEqual(stop.cause, 'would suspend')
        w2, w1 = self.manip_check(m, fr, [self.MANIP_W2, self.MANIP_W1])
        self.assertEqual(history(m, w2), then)
        self.assertEqual(history(m, w1), prompt)
        self.assertEqual(windev.read_cells(fr, 603, 520, 40, 4), ['Enter FEP node name--------->', 'local',
                                                                  'Enter your PIMOS user name-->', '#'])
        # a click on window 1's uncovered part: it comes to the top,
        # selected, and the next line is its own
        m, fr, stop = self.later_run(E['login'], E['two'], self.keys('local'),
                                     [FB.mouse('l', 1100, 600)] + self.keys('local'))
        self.assertEqual(stop.cause, 'would suspend')
        w1, w2 = self.manip_check(m, fr, [self.MANIP_W1, self.MANIP_W2])
        self.assertIs(m.get_slot(C, 'selected'), w1)
        self.assertEqual(history(m, w1), then)
        self.assertEqual(history(m, w2), then)
        self.assertEqual(windev.read_cells(fr, 758, 564, 40, 4), ['Enter FEP node name--------->', 'local',
                                                                  'Enter your PIMOS user name-->', '#'])
        self.assertEqual(self.band(fr)[2], ['standard_io_window/1'])

    def test_win_m7_manip(self):
        # M7, the window manipulator (coordinator.esp "THE MANIPULATOR",
        # "THE STACK"; window_pane.esp lift/1, lay/1, move_to/3).  Items
        # verbatim from TM-125 p8 (PRINTED-INTERFACE, window.md §4.4):
        # SHOW "show the whole of a partly shown window", HIDE "move it to
        # the bottom of the window list", RESHAPE "point at the top-left
        # and bottom-right corners with the mouse", MOVE "move by mouse";
        # the others are not offered (OURS).  It opens on the middle button
        # over a window, for that window (OURS: TM-125 puts it on the
        # system menu, whose held login.com items have no such entry; the
        # middle button moves a pimfep window, USAGE window.md §5.3).
        # Restacking keeps each hidden part in save areas and copies
        # between them and the frame (PROSE TM-225 p10, TM-126 p5,
        # window.md §4.1).  Each case is compared with a frame built
        # without the manipulator:
        #   - HIDE window 2: window 1 whole over it, selected (INFERENCE,
        #     TM-225 p11: the selected window is the top), window 2's
        #     cursor off: `two` with window 1's rectangle and the band's
        #     box from `before`, window 2's block cursor off;
        #   - SHOW after HIDE: exactly `two` (the plan's pin: HIDE then
        #     SHOW restores the covered window's dots);
        #   - kill window 2 while it lies under window 1 (README "Open"
        #     until M7: its save area put stale dots over window 1): the
        #     frame of a run that never made window 2, with the same line
        #     typed into window 1;
        #   - MOVE window 2 to (100, 100): the frame of a run that made it
        #     there;
        #   - MOVE the covered window 1 to (100, 100): `before` with window
        #     1 moved, window 2 whole from `two`, its cursor off;
        #   - output to covered window 2 (permission `out`): the frame of
        #     the same output written while window 2 was on top;
        #   - RESHAPE window 2 to (100, 100)-(500, 300): a new pane of
        #     35 x 12 cells there with its title and transcript (the held
        #     callback has_been_reshaped/1 sent after reshape/5,
        #     standard_io_window OURS bodies), and outside it the frame
        #     with window 2 gone.
        # After each, save memory holds the windows' own areas only, every
        # command is OK and the stream replays to the frame.
        # Window M7's rest (2026-11-26) moved this test's pins: the
        # manipulator has eight items, so its height is 87 -> 151 and the
        # `manip` screen changed; nothing else here moved.
        # Injections, OBSERVED (2026-11-26, at the final code; each from a backup copy,
        # restored by copy, cmp clean; Window, test_fep_bridge.py and
        # test_kl0.py run, test_kl0.py OK in each, all else OK):
        #   F1b step 3m's keyboard back (typed/2 and the read on the
        #       coordinator's one stream, the read gated on selection, no
        #       type-ahead): test_win_m7_keyboard_focus and this test FAIL.
        #   F1  the same with M7's type-ahead kept (it then puts each key
        #       back on the stream it takes it from): M4, the bridged and
        #       login screens, M6 selection, the console move, keyboard
        #       focus and this test FAIL or ERROR, and test_fep_bridge.py
        #       test_replay and test_login_service_and_login.
        #   F2  type_ahead/2 a no-op: M4, the bridged and login screens, M6
        #       selection and the console move FAIL, and test_fep_bridge.py
        #       test_replay and
        #       test_login_service_and_login (their keys are queued before
        #       the requester's window is selected).
        #   F3  a selection does not raise its window: keyboard focus and
        #       this test FAIL.
        #   M1  lift/1 skips the save-area restore (the plan's injection):
        #       keyboard focus and this test FAIL.
        #   M2  take_off/2 lifts nothing (M6's kill): this test only.
        #   M3  HIDE lays the hidden window last, on top: this test only.
        #   M4  move_to/3 does not draw the old place's under-area back:
        #       this test and test_win_m7_console_move.
        #   M5  has_been_reshaped/1 draws no transcript: this test only.
        #   M6  the overlap test never finds one (nothing is lifted):
        #       keyboard focus and this test FAIL.
        #   M7  uncover/3 lifts nothing (no `out` permission): this test
        #       only (the covered-output case).
        #   M8  MOVE and RESHAPE send no has_been_reshaped/1:
        #       test_win_m7_console_move and this test (the RESHAPE).
        import windev
        import winfb
        E = self.manip_events()
        C = K.ClassRef('simpos##coordinator')
        login = E['login']
        m, before, _ = self.later_run(login)
        m, two, _ = self.later_run(login, E['two'])
        w2, w1 = self.manip_check(m, two, [self.MANIP_W2, self.MANIP_W1])
        p2 = m.get_slot(w2, 'pane')
        cur2 = [m.get_slot(p2, 'cx'), m.get_slot(p2, 'cy'), 11, 14]
        self.assertEqual(cur2, [603, 534, 11, 14])
        # the manipulator, at the middle button
        m, menu, stop = self.later_run(login, E['two'], E['menu'])
        self.assertEqual(stop.cause, 'would suspend')
        P = m.get_slot(C, 'menu_pane')
        self.assertEqual([K.resolve(m.get_slot(P, k)) for k in ('x', 'y', 'w', 'h', 'items_top')],
                         [620, 560, 224, 167, 581])     # window M9: 151 -> 167, ATTRIBUTE added
        self.assertEqual(windev.read_cells(menu, 633, 563, 18, 1), ['WINDOW MANIPULATOR'])
        for i, label in enumerate(('SHOW', 'HIDE', 'RESHAPE', 'MOVE', 'EXPAND', 'MENU', 'PERMISSION',
                                   'ATTRIBUTE', 'EXIT')):
            n = len(label)
            self.assertEqual(windev.read_cells(menu, 622 + (220 - 11 * n) // 2, 582 + 16 * i, n, 1), [label])
        self.assertEqual((windev.pbm_sha256(menu), menu.count()), self.SHOT_PINS['manip'])
        # HIDE
        m, hidden, stop = self.later_run(login, E['two'], E['hide'])
        self.assertEqual(stop.cause, 'would suspend')
        w1h, w2h = self.manip_check(m, hidden, [self.MANIP_W1, self.MANIP_W2])
        self.assertIs(m.get_slot(C, 'selected'), w1h)
        want = winfb.Frame()
        want.rows = list(two.rows)
        want.command(winfb.FILL << 4 | 2, cur2 + [0, 0])
        self.paste(want, before, *self.MANIP_W1)
        self.paste(want, before, *self.BOX_AT)
        self.assertEqual(hidden.rows, want.rows)
        self.assertEqual((windev.pbm_sha256(hidden), hidden.count()), self.SHOT_PINS['hidden'])
        # SHOW after HIDE: the frame before the HIDE
        m, shown, stop = self.later_run(login, E['two'], E['hide'], E['show'])
        ws = self.manip_check(m, shown, [self.MANIP_W2, self.MANIP_W1])
        self.assertIs(m.get_slot(C, 'selected'), ws[0])
        self.assertEqual(shown.rows, two.rows)
        # kill the covered window 2, after a line typed into window 1
        m, alone, _ = self.later_run(login, self.keys('local'))
        m, killed, stop = self.later_run(login, E['two'], E['hide'], self.keys('local'), E['kill'])
        self.assertEqual(stop.cause, 'would suspend')
        self.manip_check(m, killed, [self.MANIP_W1])
        self.assertEqual(killed.rows, alone.rows)
        # output to a covered window (permission `out`, window_pane.esp's
        # head): the line typed into window 2 and the click raising window
        # 1 in one batch, so window 2 echoes and prompts while covered: the
        # frame of the same events in two batches (written before the raise)
        from fep_bridge import mouse
        m, late, stop = self.later_run(login, E['two'], self.keys('local') + [mouse('l', 1100, 600)])
        self.manip_check(m, late, [self.MANIP_W1, self.MANIP_W2])
        m, early, _ = self.later_run(login, E['two'], self.keys('local'), [mouse('l', 1100, 600)])
        self.assertEqual(late.rows, early.rows)
        # MOVE window 2 (the top one)
        m, moved, stop = self.later_run(login, E['two'], E['move'])
        self.manip_check(m, moved, [[100, 100, 446, 121], self.MANIP_W1])
        m, made, _ = self.later_run(login, E['two_at_100'])
        self.assertEqual(moved.rows, made.rows)
        # MOVE the covered window 1
        m, moved1, stop = self.later_run(login, E['two'], E['move1'])
        w1m, w2m = self.manip_check(m, moved1, [[100, 100, 446, 121], self.MANIP_W2])
        self.assertIs(m.get_slot(C, 'selected'), w1m)
        want = winfb.Frame()
        want.rows = list(before.rows)
        want.command(winfb.FILL << 4 | 1, self.MANIP_W1 + [0, 0])
        self.paste(want, two, *self.MANIP_W2)
        want.command(winfb.FILL << 4 | 2, cur2 + [0, 0])
        self.paste(want, before, *self.MANIP_W1, dx=100, dy=100)
        self.assertEqual(moved1.rows, want.rows)
        # RESHAPE window 2: the outline (201 x 151), then the new pane
        m, band, _ = self.later_run(login, E['two'], E['reshape_band'])
        self.assertEqual(sum(bin(a ^ b).count('1') for a, b in zip(two.rows, band.rows)), 2 * 201 + 2 * (151 - 2))
        m, reshaped, stop = self.later_run(login, E['two'], E['reshape'])
        self.assertEqual(stop.cause, 'would suspend')
        w2r, _w1 = self.manip_check(m, reshaped, [[100, 100, 391, 191], self.MANIP_W1])
        q = m.get_slot(w2r, 'pane')
        self.assertEqual([m.get_slot(q, k) for k in ('cols', 'rows')], [35, 12])
        self.assertEqual(self._walk(m.get_slot(w2r, 'place')), [100, 100, 401, 201])
        self.assertEqual(windev.read_cells(reshaped, 103, 103, 35, 1), ['Pimos remote login 6'])
        self.assertEqual(windev.read_cells(reshaped, 103, 120, 35, 2), ['Enter FEP node name--------->', '#'])
        self.assertEqual(self.band(reshaped)[2], ['standard_io_window/2'])
        want = winfb.Frame()
        want.rows = list(before.rows)
        want.command(winfb.FILL << 4 | 2, [758, 578, 11, 14, 0, 0])      # window 1's cursor off
        self.paste(want, two, *self.BOX_AT)                              # the box names window 2
        self.paste(want, reshaped, 100, 100, 391, 191)
        self.assertEqual(reshaped.rows, want.rows)
        self.assertEqual((windev.pbm_sha256(reshaped), reshaped.count()), self.SHOT_PINS['reshaped'])

    def test_win_m7_console_move(self):
        # M7, MOVE and RESHAPE on PIMOS's console (the M4 run replayed from
        # its tape), whose window class is the HELD pimfep##pimos_window
        # on the pmacs_window stand-in: the manipulator sends reshape/5
        # (stand-in: the window's place) and has_been_reshaped/1, whose
        # stand-in body redraws the window at its new place (drawn_again:
        # a new pane, the buffer's text).  The tape's user script is fixed,
        # so after the replay the mouse events are given straight to the
        # coordinator's event/2 (OURS harness).  MOVE by the middle button
        # at (300, 300), MOVE at y 376, the place (100, 100): the frame
        # equals the replay's with the console's rectangle cleared and its
        # dots put at (100, 100); a new pane was made (has_been_reshaped/1
        # ran); the window's own place is (100, 100).  RESHAPE then to
        # (50, 50)-(400, 300): since window M7's text size, the console's
        # text size becomes the 31 x 16 cells that fit, and the buffer is
        # drawn again wrapped to it (until then the console moved with its
        # size kept, 523 x 219 at (50, 50): that pin moved).
        # Injections, OBSERVED: see test_win_m7_manip's header (F1, F2, M4
        # and M8 fail this test).
        import fep_bridge as FB
        import windev
        import winfb
        psi, _t = self.console()
        m = psi.m
        C = K.ClassRef('simpos##coordinator')
        fr = windev.device(m).frame
        before = winfb.Frame()
        before.rows = list(fr.rows)
        con, login = self._walk(m.get_slot(C, 'windows'))
        self.assertEqual(con.cid, 'pimfep##pimos_window')
        old = m.get_slot(con, 'pane')
        self.assertEqual([m.get_slot(old, k) for k in ('x', 'y', 'w', 'h')], [200, 200, 523, 219])
        L = FB.mouse

        def events(*evs):
            for ev in evs:
                K.call_class_method(m, 'simpos##coordinator', 'event', [ev])
        events(L('m', 300, 300), L('l', 380, 376), K.Vec([K.Atom('move'), 150, 150]), L('l', 100, 100))
        new = m.get_slot(con, 'pane')
        self.assertIsNot(new, old)
        self.manip_check(m, fr, [[100, 100, 523, 219], self.MANIP_W1])
        self.assertEqual((m.get_slot(con, 'x'), m.get_slot(con, 'y')), (100, 100))
        want = winfb.Frame()
        want.rows = list(before.rows)
        want.command(winfb.FILL << 4 | 1, [200, 200, 523, 219, 0, 0])
        self.paste(want, before, 200, 200, 523, 219, dx=100, dy=100)
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual(windev.read_cells(fr, 103, 103, 13, 1), ['PIMOS CONSOLE'])
        events(L('m', 300, 300), L('l', 380, 360), L('l', 50, 50), L('l', 400, 300))
        # RESHAPE to 351 x 251 dots: the text size the cells that fit,
        # (351 - 6) / 11 = 31 by (251 - 23) / 14 = 16 (pmacs_window
        # reshape/5, window M7); the pane 347 x 247; the buffer's text
        # drawn again in it, wrapped at 31 columns
        self.manip_check(m, fr, [[50, 50, 347, 247], self.MANIP_W1])
        self.assertEqual([m.get_slot(con, k) for k in ('columns', 'rows')], [31, 16])
        q = m.get_slot(con, 'pane')
        self.assertEqual([m.get_slot(q, k) for k in ('cols', 'rows')], [31, 16])
        self.assertEqual(windev.read_cells(fr, 53, 53, 13, 1), ['PIMOS CONSOLE'])
        self.assertEqual(windev.read_cells(fr, 53, 70, 31, 5), [
            'Shell>> pwd', ' The value of task: directory i', 's ">sys>user>pmpsi" .', 'Shell>> #', ''])
        want = winfb.Frame()
        want.rows = list(before.rows)
        want.command(winfb.FILL << 4 | 1, [200, 200, 523, 219, 0, 0])
        self.paste(want, fr, 50, 50, 347, 247)
        self.assertEqual(fr.rows, want.rows)

    def test_win_m7_permissions(self):
        # M7, output permission (coordinator.esp "OUTPUT PERMISSION";
        # window.md §4.1).  The four kinds are PROSE TM-125 p5-6 and
        # TM-225 p10-11 (①-④); the ATTRIBUTE dialogue lists them as `out
        # / wait / show / notify` (SCREENSHOT TM-125 p7 Fig. 4); held code
        # spells the create option `permission(out|show)` and sends
        # set_permission/2 (USAGE).  The manipulator's PERMISSION item
        # ("reset the window output permission by sub-menu", TM-125 p8)
        # sets window 2's.  In each case window 2 is selected, `local` is
        # typed into it and, in the same batch, a click raises window 1
        # over it (manip_events' `late`), so window 2 echoes while
        # covered:
        #   - wait (①, "the writer waits until the window is shown"): the
        #     frame is that of the click alone (`nokeys`: no echo), the
        #     writer is held back; SHOW then raises window 2 and the
        #     writer goes on: the frame of the keys typed with window 2 on
        #     top (`typed`);
        #   - show (③, "force the window shown, then write; this changes
        #     the selected window"): `typed` at once, window 2 selected,
        #     the band's box names it, and the next line goes to it;
        #   - notify (④, "a temporary window lets the user choose ① or ③
        #     by mouse"): a pop-up at the mouse titled with the window's
        #     title (OURS), `wait` and `show`; `show`: `typed`; `wait`:
        #     `nokeys`, the writer still held back (marked notified).
        # The look of the notify window is OURS (no source shows one); its
        # place (the mouse) is TM-125 p6-7's temporary window.
        # Injections, OBSERVED: see test_win_m7_items's header.
        import fep_bridge as FB
        import windev
        E = self.manip_events()
        C = K.ClassRef('simpos##coordinator')
        L = FB.mouse
        login, two, late = E['login'], E['two'], E['late']
        # the submenu, at the mouse
        m, sub, stop = self.later_run(login, two, E['permission'])
        P = m.get_slot(C, 'menu_pane')
        self.assertEqual([K.resolve(m.get_slot(P, k)) for k in ('x', 'y', 'w', 'h', 'items_top')],
                         [700, 684, 136, 87, 705])
        for i, label in enumerate(('out', 'wait', 'show', 'notify')):
            n = len(label)
            self.assertEqual(windev.read_cells(sub, 702 + (132 - 11 * n) // 2, 706 + 16 * i, n, 1), [label])
        self.assertEqual(windev.read_cells(sub, 702 + (132 - 110) // 2, 687, 10, 1), ['PERMISSION'])
        for name in ('out', 'wait', 'show', 'notify'):
            m, _f, _s = self.later_run(login, two, self.permission(name))
            self.assertEqual(m.get_slot(self._walk(m.get_slot(C, 'windows'))[0], 'permission'), K.Atom(name))

        def waiters(m):
            return [K.resolve(self._walk(w)[2]) for w in self._walk(m.get_slot(C, 'waiters'))]
        for name in ('wait', 'show', 'notify'):
            perm = self.permission(name)
            m, nokeys, _ = self.later_run(login, two, perm, [L('l', 1100, 600)])
            m, typed, _ = self.later_run(login, two, perm, self.keys('local'))
            self.manip_check(m, typed, [self.MANIP_W2, self.MANIP_W1])
            m, fr, stop = self.later_run(login, two, perm, late)
            self.assertEqual(stop.cause, 'would suspend', name)
            if name == 'wait':
                self.manip_check(m, fr, [self.MANIP_W1, self.MANIP_W2])
                self.assertEqual(fr.rows, nokeys.rows)
                self.assertEqual(waiters(m), [K.Atom('wait')])
                m, fr, _ = self.later_run(login, two, perm, late, [L('m', 620, 560), L('l', 700, 588)])
                self.manip_check(m, fr, [self.MANIP_W2, self.MANIP_W1])
                self.assertEqual((fr.rows, waiters(m)), (typed.rows, []))
            elif name == 'show':
                w2, _w1 = self.manip_check(m, fr, [self.MANIP_W2, self.MANIP_W1])
                self.assertEqual(fr.rows, typed.rows)
                self.assertIs(m.get_slot(C, 'selected'), w2)
                self.assertEqual(self.band(fr)[2], ['standard_io_window/2'])
                m, fr, _ = self.later_run(login, two, perm, late, self.keys('pimos'))
                self.manip_check(m, fr, [self.MANIP_W2, self.MANIP_W1])
                self.assertEqual(windev.read_cells(fr, 603, 520, 40, 5),
                                 ['Enter FEP node name--------->', 'local', 'Enter your PIMOS user name-->',
                                  'pimos', 'Enter your PIMOS password--->'])
            else:
                M = m.get_slot(C, 'menu_pane')
                self.assertEqual([K.resolve(m.get_slot(M, k)) for k in ('x', 'y', 'w', 'h', 'items_top')],
                                 [1034, 600, 246, 55, 621])
                self.assertEqual(windev.read_cells(fr, 1036, 603, 22, 1), [' Pimos remote login 6'])
                self.assertEqual([windev.read_cells(fr, 1036 + 99, 622 + 16 * i, 4, 1)[0] for i in (0, 1)],
                                 ['wait', 'show'])
                self.assertEqual(waiters(m), [K.Atom('notified')])
                self.assertEqual(K.resolve(m.get_slot(C, 'dialogue')).args[0], K.Atom('notify'))
                self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.SHOT_PINS['notify'])
                m, fr, _ = self.later_run(login, two, perm, late, [L('l', 1100, 621 + 7 + 16)])
                self.manip_check(m, fr, [self.MANIP_W2, self.MANIP_W1])
                self.assertEqual((fr.rows, waiters(m)), (typed.rows, []))
                m, fr, _ = self.later_run(login, two, perm, late, [L('l', 1100, 621 + 7)])
                self.manip_check(m, fr, [self.MANIP_W1, self.MANIP_W2])
                self.assertEqual((fr.rows, waiters(m)), (nokeys.rows, [K.Atom('notified')]))

    def test_win_m7_popup_over_writer(self):
        # M7, a window that writes under an open pop-up or a sweep's
        # outline (README "Open" until this test: the windows lifted for
        # the write drew back their under-areas over the menu, and text
        # was drawn into the exclusive_or outline).  Window 2 (permission
        # out) echoes `local` while window 1 covers it (manip_events'
        # `late`) and, in the same batch:
        #   - the system menu is opened over both at (620, 510): the frame
        #     equals the run where the menu is opened after the echo, and
        #     after a click off its items it equals `late` without the
        #     menu.  The pop-up is lifted first and laid back last
        #     (coordinator uncover/3, menu_pane lift/1, lay/1: a temporary
        #     window is "never hidden by an ordinary window" and saves
        #     what it covers, PROSE TM-125 p6-7);
        #   - MOVE of window 1 is begun, its outline across window 2's
        #     echo row (at (610, 540)): the
        #     frame equals the run where the outline is drawn after the
        #     echo (the outline is taken off around the write).
        # Injections, OBSERVED: see test_win_m7_items's header.
        import fep_bridge as FB
        E = self.manip_events()
        L = FB.mouse
        C = K.ClassRef('simpos##coordinator')
        login, two, late = E['login'], E['two'], E['late']
        rr = L('rr', 620, 510)
        m, a, _ = self.later_run(login, two, late + [rr])
        self.assertNotEqual(m.get_slot(C, 'menu_pane'), 0)
        self.assertEqual(len(self._walk(m.get_slot(K.ClassRef('simpos##save_memory'), 'used'))), 3)
        m, b, _ = self.later_run(login, two, late, [rr])
        self.assertEqual(a.rows, b.rows)
        m, closed, _ = self.later_run(login, two, late + [rr], [L('l', 625, 515)])
        self.manip_check(m, closed, [self.MANIP_W1, self.MANIP_W2])
        m, plain, _ = self.later_run(login, two, late)
        self.assertEqual(closed.rows, plain.rows)
        sweep = [L('m', 1100, 600), L('l', 1180, 676), K.Vec([K.Atom('move'), 610, 540])]
        m, a, _ = self.later_run(login, two, late + sweep)
        self.assertEqual(self._walk(m.get_slot(C, 'outline')), [610, 540, 446, 121])
        m, b, _ = self.later_run(login, two, late, sweep)
        self.assertEqual(a.rows, b.rows)

    def test_win_m7_items(self):
        # M7, the manipulator's items after SHOW, HIDE, RESHAPE and MOVE,
        # in TM-125 p8's order (PRINTED-INTERFACE): EXPAND, MENU,
        # PERMISSION (test_win_m7_permissions), EXIT.  ATTRIBUTE (the
        # Fig. 4 choice window: window M9), HARDCOPY (no printer is
        # modelled) and SUPERIOR / INFERIOR (no window hierarchy: every
        # window is the screen's inferior) are not offered (README).
        #   - EXPAND "expand the window size as large as possible but not
        #     hide another fully shown window": window 2, moved to (100,
        #     100) clear of window 1, grows to (0, 0)-(1280, 544), its
        #     bottom stopped by window 1 (OURS order: left, right, up,
        #     down): a pane of 115 x 37 cells; outside it the frame
        #     equals `before` with window 1's cursor off and the box
        #     naming window 2 (as RESHAPE's);
        #   - MENU "select the window using the submenu of windows list":
        #     a pop-up titled `WINDOWS` (OURS) listing the windows by
        #     title, top first; choosing window 1 selects and raises it:
        #     the frame of HIDE on window 2;
        #   - EXIT "exit from window manipulator": the frame before the
        #     manipulator opened.
        # Injections, OBSERVED (2026-11-26, at the final code; each from a
        # backup copy, restored by copy, cmp clean; Window,
        # test_fep_bridge.py and test_kl0.py run, all else OK):
        #   P1 wake/1 a no-op (a held-back writer never goes on):
        #      test_win_m7_permissions FAILS, nothing else.
        #   P2 held_back/3 lets `wait` write at once (as out):
        #      test_win_m7_permissions FAILS, nothing else.
        #   P3 held_back/3's `show` neither raises nor selects (it writes
        #      as out): test_win_m7_permissions FAILS, nothing else.
        #   P4 offer/1 never opens a notify window:
        #      test_win_m7_permissions ERRORS, nothing else.
        #   P5 uncover/3 leaves an open pop-up in place:
        #      test_win_m7_popup_over_writer FAILS, nothing else.
        #   P6 uncover/3 leaves the outline in place:
        #      test_win_m7_popup_over_writer FAILS, nothing else (first
        #      run with the outline at (600, 480): it crossed no echoed
        #      text and nothing failed; moved to (610, 540), across the
        #      echo row).
        #   P7 EXPAND finds no obstacle: this test FAILS, nothing else.
        #   P8 select_window/2 sends no has_been_selected/1:
        #      test_win_m7_has_been_selected FAILS, nothing else.
        #   P9 pmacs_window reshape/5 leaves the text size alone (M7's
        #      way): test_win_m7_console_move FAILS, nothing else.
        import fep_bridge as FB
        import windev
        import winfb
        E = self.manip_events()
        C = K.ClassRef('simpos##coordinator')
        L = FB.mouse
        login, two = E['login'], E['two']
        m, before, _ = self.later_run(login)
        m, fr, stop = self.later_run(login, two, E['move'], E['expand'])
        self.assertEqual(stop.cause, 'would suspend')
        w2, _w1 = self.manip_check(m, fr, [[0, 0, 1271, 541], self.MANIP_W1])
        self.assertEqual(self._walk(m.get_slot(w2, 'place')), [0, 0, 1280, 544])
        q = m.get_slot(w2, 'pane')
        self.assertEqual([m.get_slot(q, k) for k in ('cols', 'rows')], [115, 37])
        self.assertEqual(windev.read_cells(fr, 3, 3, 40, 1), ['Pimos remote login 6'])
        self.assertEqual(windev.read_cells(fr, 3, 20, 40, 2), ['Enter FEP node name--------->', '#'])
        m, two_fr, _ = self.later_run(login, two)
        want = winfb.Frame()
        want.rows = list(before.rows)
        want.command(winfb.FILL << 4 | 2, [758, 578, 11, 14, 0, 0])      # window 1's cursor off
        self.paste(want, two_fr, *self.BOX_AT)                           # the box names window 2
        self.paste(want, fr, 0, 0, 1271, 541)
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.SHOT_PINS['expand'])
        # MENU
        m, fr, _ = self.later_run(login, two, E['windows'])
        M = m.get_slot(C, 'menu_pane')
        self.assertEqual([K.resolve(m.get_slot(M, k)) for k in ('x', 'y', 'w', 'h', 'items_top')],
                         [700, 668, 246, 55, 689])
        self.assertEqual(windev.read_cells(fr, 702 + (242 - 77) // 2, 671, 7, 1), ['WINDOWS'])
        self.assertEqual([windev.read_cells(fr, 713, 690 + 16 * i, 20, 1)[0] for i in (0, 1)],
                         ['Pimos remote login 6', 'Pimos remote login 5'])
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.SHOT_PINS['windows'])
        m, fr, _ = self.later_run(login, two, E['windows'] + [L('l', 750, 689 + 7 + 16)])
        w1, _w2 = self.manip_check(m, fr, [self.MANIP_W1, self.MANIP_W2])
        self.assertIs(m.get_slot(C, 'selected'), w1)
        m, hidden, _ = self.later_run(login, two, E['hide'])
        self.assertEqual(fr.rows, hidden.rows)
        # EXIT
        m, fr, _ = self.later_run(login, two, E['exit'])
        self.manip_check(m, fr, [self.MANIP_W2, self.MANIP_W1])
        self.assertEqual(fr.rows, two_fr.rows)

    PROBE_WINDOW = """
class probe_window has
nature standard_io_window;
instance
attribute seen := [];
after:has_been_selected(W) :- W!seen := [selected | W!seen];
end."""

    def test_win_m7_has_been_selected(self):
        # M7, the select notifier's callback has_been_selected/1
        # (window.md §2.1, §2.12: kappa pbwin's after-demon on it proves a
        # SIMPOS primary; paragraph profiler_view_window defines its own):
        # the coordinator sends it once a window becomes the selected one
        # (select_window/2), not again while it stays selected; the
        # stand-ins' default primary does nothing (OURS).  The receiver is
        # a test class with an after-demon, as kappa's (OURS harness: no
        # held window on the FEP route has one), made at (100, 100) after
        # the Login PIMOS run, its events given straight to the
        # coordinator's event/2.  show/1 selects it (one call), a click on
        # the Login PIMOS window selects that one (none), a click on the
        # probe selects it again (two), and a second click changes
        # nothing.
        # Injection, OBSERVED: P8 in test_win_m7_items's header.
        import fep_bridge as FB
        ts, failed = espc.compile_text(self.PROBE_WINDOW, 'simpos')
        self.assertEqual(failed, {})
        m, _fr, _ = self.later_run(self.manip_events()['login'])
        for t in ts:
            m.lib.add(t)
        m.reset()
        opts = K.Cons(K.Vec([K.Atom('position'), 100, 100]), K.NIL)
        ((_o, w),) = K.call_class_method(m, 'simpos##probe_window', 'create', [opts, K.Var()])
        self.assertTrue(self.send(m, w, 'show'))
        C = K.ClassRef('simpos##coordinator')

        def seen():
            return len(self._walk(m.get_slot(w, 'seen'))), m.get_slot(C, 'selected') is w

        def click(x, y):
            K.call_class_method(m, 'simpos##coordinator', 'event', [FB.mouse('l', x, y)])
            return seen()
        self.assertEqual(seen(), (1, True))
        self.assertEqual(click(1100, 600), (1, False))
        self.assertEqual(click(200, 150), (2, True))
        self.assertEqual(click(200, 150), (2, True))

    def test_win_m7_permission_change(self):
        # M7, a held-back writer woken when its window's permission changes
        # (coordinator wake/1: free when out or show), and the create
        # option.  Window 2 (wait) is covered while it echoes `local`
        # (manip_events' `late`); the manipulator on its uncovered part
        # then sets its permission:
        #   - out: the writer goes on at once into the covered window (the
        #     windows above lifted): the frame equals the run with `out`
        #     set before the echo, window 1 still on top, no waiter;
        #   - show: the writer goes on as show's (window 2 raised and
        #     selected), no waiter.
        # The create option permission(P) (window.md §4.1; USAGE 63 `out`,
        # 13 `show`), as ESP builds it {permission, P}: a standard_io_window
        # made with permission(wait) holds wait; an unknown one gives out.
        # pmacs_window does not read the option (OURS: no held pmacs caller
        # gives one); its set_permission/2 does set it.
        # A killed window's waiter is dropped (remove_window/2): window 2,
        # held back under `wait`, killed by create/kill's sweep leaves no
        # waiter and opens no notify window.
        # Injections, OBSERVED: see test_win_m8_markers's header (P10-P13).
        E = self.manip_events()
        C = K.ClassRef('simpos##coordinator')
        login, two, late = E['login'], E['two'], E['late']
        wait, out, show = (self.permission(n) for n in ('wait', 'out', 'show'))

        def waiters(m):
            return [K.resolve(self._walk(w)[2]) for w in self._walk(m.get_slot(C, 'waiters'))]
        m, held, _ = self.later_run(login, two, wait, late)
        self.assertEqual(waiters(m), [K.Atom('wait')])
        m, fr, _ = self.later_run(login, two, wait, late, out)
        self.manip_check(m, fr, [self.MANIP_W1, self.MANIP_W2])
        self.assertEqual(waiters(m), [])
        m, plain, _ = self.later_run(login, two, out, late)
        self.assertEqual(fr.rows, plain.rows)
        self.assertNotEqual(fr.rows, held.rows)
        m, fr, _ = self.later_run(login, two, wait, late, show)
        w2, _w1 = self.manip_check(m, fr, [self.MANIP_W2, self.MANIP_W1])
        self.assertIs(m.get_slot(C, 'selected'), w2)
        self.assertEqual(waiters(m), [])
        # a killed window's waiter
        m, fr, _ = self.later_run(login, two, wait, late, E['kill'])
        self.assertEqual(len(self._walk(m.get_slot(C, 'windows'))), 1)
        self.assertEqual((waiters(m), m.get_slot(C, 'menu_pane')), ([], 0))
        # the create option
        for opt, want in ((K.Atom('wait'), 'wait'), (K.Atom('loud'), 'out')):
            opts = K.Cons(K.Vec([K.Atom('permission'), opt]), K.NIL)
            ((_o, w),) = K.call_class_method(m, 'simpos##standard_io_window', 'create', [opts, K.Var()])
            self.assertEqual(m.get_slot(w, 'permission'), K.Atom(want))

    PROBE_WRITER = """
class probe_writer has
nature standard_io_window;
instance
attribute partner := 0;
after:has_been_selected(W) :- P = W!partner, :putl(P, "selected");
end."""

    def test_win_m7_coordinator_writes(self):
        # M7's rest, the coordinator's own process is never held back
        # (coordinator.esp "OUTPUT PERMISSION", held_back/3's manager/1):
        # a window's has_been_selected/1 runs in the coordinator's process
        # (select_window/2, sent on a click), and here it writes into a
        # covered window whose permission is wait.  The receiver is a test
        # class whose after-demon on has_been_selected/1 puts a line on its
        # partner (OURS harness, as test_win_m7_has_been_selected: kappa
        # pbwin.esp:72 is the held after-demon on the selector; the
        # commented-out kappa sheet_obj.esp:433-438 draws in another window
        # from it).  The windows are made after the Login PIMOS run: A at
        # (100, 100) with permission(wait), shown, B over part of it
        # (activated, so A stays selected), the probe at
        # (700, 100) with A its partner; the probe is shown (show/1 selects
        # it) while `simpos##process`'s current process is the
        # coordinator's (OURS: the direct send stands for the coordinator
        # process's own event/2).  The line goes into A at once (B lifted
        # and laid back, its dots unchanged; A's uncovered columns show
        # it), with no waiter.  With the current process another one (any
        # writer), the same line waits (a waiter on A, kind wait).
        # Injection, OBSERVED: P13 in test_win_m8_markers's header.
        import windev
        A = K.Atom
        ts, failed = espc.compile_text(self.PROBE_WRITER, 'simpos')
        self.assertEqual(failed, {})
        m, _fr, _ = self.later_run(self.manip_events()['login'])
        for t in ts:
            m.lib.add(t)
        m.reset()
        fr = windev.device(m).frame
        C = K.ClassRef('simpos##coordinator')
        PC = K.ClassRef('simpos##process')

        def made(cid, x, y, *more):
            opts = K.NIL
            for o in reversed((K.Vec([A('position'), x, y]),) + more):
                opts = K.Cons(o, opts)
            ((_o, v),) = K.call_class_method(m, cid, 'create', [opts, K.Var()])
            return v
        a = made('simpos##standard_io_window', 100, 100, K.Vec([A('permission'), A('wait')]))
        self.assertTrue(self.send(m, a, 'show'))
        b = made('simpos##standard_io_window', 200, 130)
        self.assertTrue(self.send(m, b, 'activate'))      # A stays selected
        pb = m.get_slot(b, 'pane')
        bx, by, bw, bh = (m.get_slot(pb, k) for k in ('x', 'y', 'w', 'h'))
        under_b = self.block(fr, bx, by, bw, bh)
        probe = made('simpos##probe_writer', 700, 100)
        m.set_slot(probe, 'partner', a)
        current = m.get_slot(PC, 'current')
        m.set_slot(PC, 'current', m.get_slot(C, 'process'))
        try:
            self.assertTrue(self.send(m, probe, 'show'))
        finally:
            m.set_slot(PC, 'current', current)
        self.assertIs(m.get_slot(C, 'selected'), probe)
        self.assertEqual(self._walk(m.get_slot(C, 'waiters')), [])
        self.assertEqual(''.join(chr(c & 0xff) for c in self._walk(m.get_slot(a, 'transcript'))[0].codes()),
                         'selected')     # the ESP string's 16-bit codes, 16#"23xx"
        self.assertEqual(self.block(fr, bx, by, bw, bh), under_b)
        pa = m.get_slot(a, 'pane')
        cw = m.get_slot(pa, 'cw')
        seen = (bx - m.get_slot(pa, 'left')) // cw
        self.assertEqual(windev.read_cells(fr, m.get_slot(pa, 'left'), m.get_slot(pa, 'top'), seen, 1),
                         ['selected'[:seen]])
        # another process's write to A waits
        self.assertNotEqual(m.get_slot(PC, 'current'), m.get_slot(C, 'process'))
        with self.assertRaises(K.Refusal) as e:
            self.send(m, a, 'putl', K.Str('later'))
        self.assertEqual(e.exception.cause, 'would suspend')
        self.assertEqual([K.resolve(self._walk(v)[2]) for v in self._walk(m.get_slot(C, 'waiters'))],
                         [A('wait')])

    # window M8, graphics (standard_io_window.esp and window_pane.esp
    # "Window M8"): a window of 40 x 20 cells made at (100, 100) after the
    # Login PIMOS run (OURS harness, as test_win_m7_has_been_selected),
    # activated, not selected (so no cursor); its inside's top-left is
    # (103, 120), 440 x 280 dots
    GRAPHICS_AT = (103, 120)

    def graphics_window(self):
        m, _fr, _ = self.later_run(self.manip_events()['login'])
        m.reset()
        opts = K.Cons(K.Vec([K.Atom('position'), 100, 100]),
                      K.Cons(K.Vec([K.Atom('size'), K.Vec([K.Atom('ch'), 40]), K.Vec([K.Atom('ch'), 20])]),
                             K.NIL))
        ((_o, w),) = K.call_class_method(m, 'simpos##standard_io_window', 'create', [opts, K.Var()])
        self.assertTrue(self.send(m, w, 'activate'))
        return m, w

    def held_draw_box(self, m, w, x, y, wd, ht):
        # the HELD paragraph##type_switch_icon local draw_box/5
        # (p_icon.esp:177-186: six draw_line commands in one
        # execute_graphics_command/2, widths 2 and 1, ops reset and set),
        # run on the compiled .ptf
        cid = 'paragraph##type_switch_icon'
        ps = {(p.name, p.arity): p for p in m.lib.templates[cid].locals}
        m.reset()
        return sum(1 for _ in m.solve((m.code(cid), ps[('draw_box', 5)].offset), [w, x, y, wd, ht]))

    def graphics_run(self):
        # the screen of psi/winshot.py's `graphics` stage: a black block,
        # the held icon box carved and drawn on it, a slanted line, a
        # string, a clipped fill and a transfer.  -> (machine, frame)
        import windev
        m, w = self.graphics_window()
        self.assertTrue(self.send(m, w, 'draw_filled_rectangle', 10, 10, 40, 60, K.Atom('set')))
        self.assertEqual(self.held_draw_box(m, w, 60, 10, 19, 37), 1)
        self.assertTrue(self.send(m, w, 'draw_line', 100, 10, 199, 59))
        self.assertTrue(self.send(m, w, 'draw_string', 100, 80, K.Str('window M8')))
        self.assertTrue(self.send(m, w, 'draw_filled_rectangle', 430, 270, 50, 50, K.Atom('set')))
        self.assertTrue(self.send(m, w, 'transfer', 60, 10, 220, 10, 19, 37, K.Atom('copy')))
        return m, windev.device(m).frame

    def test_win_m8_graphics(self):
        # M8, graphics (window.md §2.5; the plan's M8 row).  Each drawing
        # is checked against a frame built from winfb commands in Python:
        #   - draw_filled_rectangle/6 with set (a 40 x 60 block at (10,
        #     10) of the inside);
        #   - the HELD paragraph##type_switch_icon draw_box/5 at (60, 10),
        #     19 x 37 (p_icon.esp:177-186, the compiled .ptf run through
        #     execute_graphics_command/2): first over the black block
        #     (its two width-2 `reset` lines carve white, its four width-1
        #     `set` lines draw nothing new), then on white (the four set
        #     lines only: (19 + 18 + 37 + 35) dots);
        #   - draw_line/5 (1 dot, solid, exclusive_or: TM-125 p17's
        #     defaults), slanted: 100 dots; drawn twice, the frame is back
        #     (the plan's "XOR twice erases");
        #   - draw_string/4 at (100, 80): read back as text;
        #   - a fill at (430, 270), 50 x 50, cut to the inside: 10 x 10;
        #   - transfer/8 (copy) of the box to (220, 10);
        #   - get_mouse_position/3 after a move to (150, 160): (47, 40);
        #   - refused loudly: a dotted line, an unknown pattern (light_paint
        #     until M8's rest: test_win_m8_patterns), a slanted line leaving
        #     the inside, an unknown command (draw_bars; draw_arc until M8's
        #     rest: test_win_m8_shapes).
        # Injections, OBSERVED (2026-11-26; each from a backup copy,
        # restored by copy, cmp clean; Window, test_fep_bridge.py and
        # test_kl0.py run, all else OK):
        #   G1 draw_line/5's default op `set` instead of exclusive_or (the plan's
        #      injection): this test FAILS, nothing else.
        #   G2 no clipping of fills to the inside: this test FAILS, nothing else.
        #   G3 execute_graphics_command/2 skips each command: this test FAILS,
        #      nothing else.
        #   G4 a horizontal line's width ignored: this test FAILS, nothing else.
        import windev
        import winfb
        X0, Y0 = self.GRAPHICS_AT
        m, w = self.graphics_window()
        fr = windev.device(m).frame
        want = winfb.Frame()
        want.rows = list(fr.rows)

        def fill(x, y, wd, ht, r):
            want.command(winfb.FILL << 4 | r, [X0 + x, Y0 + y, wd, ht, 0, 0])

        def box(x, y, wd, ht, carve):
            if carve:
                fill(x, y + 1, wd, 2, 1)
                fill(x, y, 2, ht, 1)
            fill(x, y + ht - 1, wd, 1, 0)
            fill(x + 1, y + ht - 2, wd - 1, 1, 0)
            fill(x + wd - 1, y, 1, ht, 0)
            fill(x + wd - 2, y + 2, 1, ht - 2, 0)
        self.assertTrue(self.send(m, w, 'draw_filled_rectangle', 10, 10, 40, 60, K.Atom('set')))
        fill(10, 10, 40, 60, 0)
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual(self.held_draw_box(m, w, 10, 10, 19, 37), 1)
        box(10, 10, 19, 37, True)
        self.assertEqual(fr.rows, want.rows)
        n0 = fr.count()
        self.assertEqual(self.held_draw_box(m, w, 60, 10, 19, 37), 1)
        box(60, 10, 19, 37, False)
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual(fr.count() - n0, 19 + 18 + 37 + 35 - 4)     # the columns cross the two rows
        # the slanted line, exclusive_or: once 100 dots, twice none
        n0 = fr.count()
        self.assertTrue(self.send(m, w, 'draw_line', 100, 10, 199, 59))
        self.assertEqual(fr.count() - n0, 100)
        self.assertTrue(self.send(m, w, 'draw_line', 100, 10, 199, 59))
        self.assertEqual(fr.rows, want.rows)
        # a string, its first letter's top-left at (100, 80)
        self.assertTrue(self.send(m, w, 'draw_string', 100, 80, K.Str('window M8')))
        self.assertEqual(windev.read_cells(fr, X0 + 100, Y0 + 80, 9, 1), ['window M8'])
        self.assertTrue(self.send(m, w, 'draw_string', 100, 80, K.Str('window M8')))
        self.assertEqual(fr.rows, want.rows)
        # a fill cut to the inside (440 x 280)
        n0 = fr.count()
        self.assertTrue(self.send(m, w, 'draw_filled_rectangle', 430, 270, 50, 50, K.Atom('set')))
        self.assertEqual(fr.count() - n0, 100)
        fill(430, 270, 10, 10, 0)
        self.assertEqual(fr.rows, want.rows)
        # transfer/8: the box copied to (220, 10)
        self.assertTrue(self.send(m, w, 'transfer', 60, 10, 220, 10, 19, 37, K.Atom('copy')))
        want.command(winfb.COPY << 4 | 3, [X0 + 60, Y0 + 10, 19, 37, X0 + 220, Y0 + 10])
        self.assertEqual(fr.rows, want.rows)
        # the mouse
        K.call_class_method(m, 'simpos##coordinator', 'event', [K.Vec([K.Atom('move'), 150, 160])])
        m.reset()
        xy = [K.Var(), K.Var()]
        self.assertTrue(any(True for _ in m.solve_send(w, 'get_mouse_position', xy + [w])))
        self.assertEqual([K.resolve(v) for v in xy], [47, 40])
        # loud refusals; the frame unchanged
        for sel, args in (('draw_line', [0, 0, 10, 0, 1, K.Atom('dotted'), K.Atom('set')]),
                          ('draw_filled_rectangle', [0, 0, 5, 5, 0, K.Atom('zigzag'), K.Atom('set')]),
                          ('draw_line', [400, 0, 460, 30]),
                          ('execute_graphics_command', [K.Cons(K.Vec([K.Atom('draw_bars'), K.Vec([1, 2])]),
                                                               K.NIL)])):
            with self.assertRaises(K.Refusal) as e:
                self.send(m, w, sel, *args)
            self.assertIn('graphics_refused', str(e.exception.detail), sel)
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual(set(fr.status), {winfb.OK})
        self.assertEqual(winfb.run_stream(windev.device(m).stream_text()).pbm(), fr.pbm())
        # the screen (psi/winshot.py `graphics`)
        m, fr = self.graphics_run()
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.GRAPHICS_PIN)

    GRAPHICS_PIN = ('f365619e8a6e34594abfe468efdd48d76fda56cc26068335ff1a4c5201154552', 107429)

    def test_win_m8_forms(self):
        # M8, the other argument forms of window.md §2.5 (each beside the
        # forms test_win_m8_graphics draws), checked against winfb-built
        # frames and dot counts:
        #   - draw_rectangle/5 (1 dot, solid, exclusive_or): the outline of
        #     30 x 20, 2*30 + 2*18 dots; twice, the frame is back;
        #   - draw_rectangle/8 with Line 2 and set: four fills inward;
        #     draw_rectangle/7 `filled` (IPSJ 36239 p5's style): the whole
        #     area, exclusive_or;
        #   - draw_line/6, the VARIANT: an integer is the width (3 dots,
        #     exclusive_or), an atom the op (`set`, 1 dot: drawn twice, it
        #     stays); draw_line/7 (Width, Style; exclusive_or);
        #   - draw_filled_rectangle/8 with pattern fix;
        #   - draw_string/5 both readings (an op name, or a font) and
        #     draw_string/6 (font, op), the font the HELD test_11 file
        #     (font create/3): read back as text;
        #   - the HELD paragraph##g_window local draw_list/8 (g_window.esp
        #     :130-158, the mono list: numbered draw_string commands of five
        #     elements, font and `set`) run on the compiled .ptf, its list
        #     given to execute_graphics_command/2 (its tail left unbound,
        #     as draw_list/8's last clause leaves it): "1 42", "2 7" at
        #     (21, 200) and (21, 218);
        #   - a slanted line leaving the inside, on a window covered by
        #     another, refuses BEFORE anything is lifted: the frame is
        #     unchanged and save memory holds no more areas than before.
        # Injections, OBSERVED: see test_win_m8_markers's header.
        import windev
        import winfb
        X0, Y0 = self.GRAPHICS_AT
        m, w = self.graphics_window()
        fr = windev.device(m).frame
        want = winfb.Frame()
        want.rows = list(fr.rows)

        def fill(x, y, wd, ht, r):
            want.command(winfb.FILL << 4 | r, [X0 + x, Y0 + y, wd, ht, 0, 0])

        def drawn(sel, *args):
            n0 = fr.count()
            self.assertTrue(self.send(m, w, sel, *args), sel)
            return fr.count() - n0
        # rectangles
        self.assertEqual(drawn('draw_rectangle', 10, 10, 30, 20), 2 * 30 + 2 * 18)
        self.assertEqual(drawn('draw_rectangle', 10, 10, 30, 20), -(2 * 30 + 2 * 18))
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual(drawn('draw_rectangle', 50, 10, 30, 20, 2, K.Atom('solid'), K.Atom('set')),
                         2 * 2 * 30 + 2 * 2 * 16)
        fill(50, 10, 30, 2, 0)
        fill(50, 28, 30, 2, 0)
        fill(50, 12, 2, 16, 0)
        fill(78, 12, 2, 16, 0)
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual(drawn('draw_rectangle', 90, 10, 30, 20, 1, K.Atom('filled')), 600)
        self.assertEqual(drawn('draw_rectangle', 90, 10, 30, 20, 1, K.Atom('filled')), -600)
        # lines: draw_line/6's two readings, draw_line/7
        self.assertEqual(drawn('draw_line', 10, 50, 59, 50, 3), 150)
        fill(10, 50, 50, 3, 2)
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual(drawn('draw_line', 10, 60, 59, 60, K.Atom('set')), 50)
        self.assertEqual(drawn('draw_line', 10, 60, 59, 60, K.Atom('set')), 0)
        fill(10, 60, 50, 1, 0)
        self.assertEqual(drawn('draw_line', 10, 70, 10, 89, 2, K.Atom('solid')), 40)
        fill(10, 70, 2, 20, 2)
        self.assertEqual(fr.rows, want.rows)
        # draw_filled_rectangle/8, pattern fix
        self.assertEqual(drawn('draw_filled_rectangle', 130, 10, 10, 10, 0, K.Atom('fix'), K.Atom('set')), 100)
        fill(130, 10, 10, 10, 0)
        self.assertEqual(fr.rows, want.rows)
        # strings: /5 an op, /5 a font, /6 a font and an op
        ((_n, font),) = K.call_class_method(m, 'simpos##font', 'create', [K.Str('font:test_11.font'), K.Var()])
        self.assertTrue(self.send(m, w, 'draw_string', 10, 100, K.Str('by op'), K.Atom('set')))
        self.assertTrue(self.send(m, w, 'draw_string', 10, 100, K.Str('by op'), K.Atom('set')))
        self.assertEqual(windev.read_cells(fr, X0 + 10, Y0 + 100, 5, 1), ['by op'])
        self.assertTrue(self.send(m, w, 'draw_string', 10, 120, K.Str('by font'), font))
        self.assertEqual(windev.read_cells(fr, X0 + 10, Y0 + 120, 7, 1), ['by font'])
        self.assertTrue(self.send(m, w, 'draw_string', 10, 120, K.Str('by font'), font))
        self.assertTrue(self.send(m, w, 'draw_string', 10, 140, K.Str('both'), font, K.Atom('exclusive_or')))
        self.assertEqual(windev.read_cells(fr, X0 + 10, Y0 + 140, 4, 1), ['both'])
        self.assertTrue(self.send(m, w, 'draw_string', 10, 140, K.Str('both'), font, K.Atom('exclusive_or')))
        self.assertTrue(self.send(m, w, 'draw_string', 10, 100, K.Str('by op'), K.Atom('reset')))
        self.assertEqual(fr.rows, want.rows)
        # the held g_window mono list
        cid = 'paragraph##g_window'
        ps = {(p.name, p.arity): p for p in m.lib.templates[cid].locals}
        m.reset()
        dl = K.Var()
        (dl,) = [K.resolve(dl) for _ in m.solve((m.code(cid), ps[('draw_list', 8)].offset),
                                                [10, 200, 1, K.Cons(42, K.Cons(7, K.NIL)), dl, font, 30, 280])]
        self.assertTrue(self.send(m, w, 'execute_graphics_command', dl))
        self.assertEqual(windev.read_cells(fr, X0 + 21, Y0 + 200, 4, 1), ['1 42'])
        self.assertEqual(windev.read_cells(fr, X0 + 21, Y0 + 218, 4, 1), ['2 7'])
        # the covered window's refused line
        m, w = self.graphics_window()
        opts = K.Cons(K.Vec([K.Atom('position'), 300, 200]), K.NIL)
        ((_o, w2),) = K.call_class_method(m, 'simpos##standard_io_window', 'create', [opts, K.Var()])
        self.assertTrue(self.send(m, w2, 'activate'))
        C = K.ClassRef('simpos##coordinator')
        self.assertIs(self._walk(m.get_slot(C, 'windows'))[0], w2)
        fr = windev.device(m).frame
        rows = list(fr.rows)
        S = K.ClassRef('simpos##save_memory')
        used = len(self._walk(m.get_slot(S, 'used')))
        with self.assertRaises(K.Refusal) as e:
            self.send(m, w, 'draw_line', 400, 0, 460, 30)
        self.assertIn('graphics_refused', str(e.exception.detail))
        self.assertEqual(fr.rows, rows)
        self.assertEqual(len(self._walk(m.get_slot(S, 'used'))), used)

    # window M8's rest: the named patterns' looks (OURS, window_pane.esp
    # named/3), a word for each of 4 rows
    NAMED_PATTERNS = {'light_paint': [0x8888, 0x2222, 0x8888, 0x2222], 'dotted': [0xAAAA, 0, 0xAAAA, 0],
                      'mesh': [0xFFFF, 0x8888, 0x8888, 0x8888],
                      'small_mesh': [0xAAAA, 0x5555, 0xAAAA, 0x5555],
                      'left_hatch': [0x8888, 0x4444, 0x2222, 0x1111],
                      'right_hatch': [0x1111, 0x2222, 0x4444, 0x8888]}

    def pattern_dot(self, p, x, y):
        # the reference: pattern P's dot at inside (X, Y), the tile
        # anchored at the inside's top-left; a pattern string a 64 x 64
        # tile of 4 words a row (INFERENCE, standard_io_window.esp
        # "PATTERNS")
        if isinstance(p, K.Atom):
            wd = self.NAMED_PATTERNS[p.name][y % 4]
        else:
            wd = p.codes()[(y % 64) * 4 + (x % 64) // 16]
        return (wd >> (15 - x % 16)) & 1

    def pattern_fill(self, want, p, x, y, wd, ht, iw=440, ih=280):
        # the reference fill (set) of P over (X, Y, WD, HT) cut to the inside
        X0, Y0 = self.GRAPHICS_AT
        for yy in range(max(y, 0), min(y + ht, ih)):
            for xx in range(max(x, 0), min(x + wd, iw)):
                if self.pattern_dot(p, xx, yy):
                    want.rows[Y0 + yy] |= 1 << (1279 - X0 - xx)

    def held_patterns(self, m):
        # the HELD paragraph##bar_v local set_pattern/2 (bar_v.esp:333-362)
        # for N = 0..5, run on the compiled .ptf
        cid = 'paragraph##bar_v'
        ps = {(p.name, p.arity): p for p in m.lib.templates[cid].locals}
        out = []
        for n in range(6):
            m.reset()
            v = K.Var()
            (got,) = [K.resolve(v) for _ in m.solve((m.code(cid), ps[('set_pattern', 2)].offset), [n, v])]
            out.append(got)
        return out

    def test_win_m8_patterns(self):
        # M8's rest, fill patterns (window.md §2.5; standard_io_window.esp
        # "PATTERNS", window_pane.esp pattern_in/7): draw_filled_rectangle/8
        # with a pattern other than fix, drawn as styled lines of the
        # frozen device line (windev line/8, winfb's style operand).
        #   - the HELD bar_v set_pattern/2 (needs blt 44, kl0_opcodes.tsv)
        #     gives light_paint, a string, dotted and three strings for N
        #     = 0..5; each string is 256 words, the set_pattern1 words each
        #     four times running;
        #   - the HELD paragraph##g_window local draw_list_b/8 (g_window.esp
        #     :160-183, the mono bar list) with those six patterns and the
        #     numbers 1..6, its list given to execute_graphics_command/2:
        #     each 17 x 11 bar equals the reference (pattern_dot: a string
        #     read as a 64 x 64 tile, 4 words a row, INFERENCE), and its
        #     number is read back beside it;
        #   - the six named patterns and a rectangle cut at the inside's
        #     left edge, against a frame built dot by dot;
        #   - exclusive_or twice erases a patterned fill;
        #   - refused loudly: an unknown pattern name, a string not of 256
        #     words; the frame unchanged.
        # Injections, OBSERVED (2026-11-26; each from a backup copy,
        # restored by copy, cmp clean; Window, test_fep_bridge.py and
        # test_kl0.py run, all else OK; rerun at the final code with the
        # Window tests, the results below):
        #   G10 styled/6 does not turn the word by the piece's column:
        #       this test, test_win_m8_shapes (its light_paint disc) and
        #       test_win_m8_rest_screen FAIL, nothing else.
        #   G11 row_words/6 reads a pattern string 1 word a row: this test
        #       and test_win_m8_rest_screen FAIL, nothing else.
        #   G12 blt 44 puts the quotient where the remainder goes: this
        #       test and test_win_m8_rest_screen FAIL, nothing else
        #       (test_kl0's census does not run set_pattern/2's values).
        import windev
        import winfb
        X0, Y0 = self.GRAPHICS_AT
        m, w = self.graphics_window()
        fr = windev.device(m).frame
        pats = self.held_patterns(m)
        self.assertEqual([p.name if isinstance(p, K.Atom) else len(p.codes()) for p in pats],
                         ['light_paint', 256, 'dotted', 256, 256, 256])
        self.assertEqual(pats[5].codes()[:8], [0x5555] * 4 + [0xAAAA] * 4)
        self.assertEqual(pats[1].codes()[:32], [0x1010] * 4 + [0] * 12 + [0x0101] * 4 + [0] * 12)
        # the held g_window mono bar list
        cid = 'paragraph##g_window'
        ps = {(p.name, p.arity): p for p in m.lib.templates[cid].locals}
        ((_n, font),) = K.call_class_method(m, 'simpos##font', 'create', [K.Str('font:test_11.font'), K.Var()])
        items = K.NIL
        for i in reversed(range(6)):
            items = K.Cons(pats[i], K.Cons(i + 1, items))
        m.reset()
        dl = K.Var()
        (dl,) = [K.resolve(dl) for _ in m.solve((m.code(cid), ps[('draw_list_b', 8)].offset),
                                                [10, 10, 1, items, dl, font, 30, 280])]
        self.assertTrue(self.send(m, w, 'execute_graphics_command', dl))

        def region(f, x, y, wd, ht):
            return [(f.rows[Y0 + y + j] >> (1280 - X0 - x - wd)) & ((1 << wd) - 1) for j in range(ht)]
        for i, p in enumerate(pats):
            y = 10 + 18 * i
            ref = winfb.Frame()
            self.pattern_fill(ref, p, 10, y + 3, 17, 11)
            self.assertEqual(region(fr, 10, y + 3, 17, 11), region(ref, 10, y + 3, 17, 11), i)
            self.assertEqual(windev.read_cells(fr, X0 + 33, Y0 + y, 1, 1), [str(i + 1)])
        # the named patterns, and one cut at the left edge
        m, w = self.graphics_window()
        fr = windev.device(m).frame
        want = winfb.Frame()
        want.rows = list(fr.rows)
        for i, name in enumerate(sorted(self.NAMED_PATTERNS)):
            p, x, y = K.Atom(name), 5 + i * 70, 5
            self.assertTrue(self.send(m, w, 'draw_filled_rectangle', x, y, 67, 83, 1, p, K.Atom('set')))
            self.pattern_fill(want, p, x, y, 67, 83)
        self.assertTrue(self.send(m, w, 'draw_filled_rectangle', -7, 100, 53, 61, 0, pats[4], K.Atom('set')))
        self.pattern_fill(want, pats[4], -7, 100, 53, 61)
        self.assertEqual(fr.rows, want.rows)
        # exclusive_or twice
        n0 = fr.count()
        self.assertTrue(self.send(m, w, 'draw_filled_rectangle', 100, 100, 77, 50, 1, pats[5],
                                  K.Atom('exclusive_or')))
        self.assertEqual(fr.count() - n0, sum(self.pattern_dot(pats[5], x, y)
                                              for x in range(100, 177) for y in range(100, 150)))
        self.assertTrue(self.send(m, w, 'draw_filled_rectangle', 100, 100, 77, 50, 1, pats[5],
                                  K.Atom('exclusive_or')))
        self.assertEqual(fr.rows, want.rows)
        # refusals
        bad = K.Str('')
        bad.set_codes([0x5555] * 16)
        for pt in (K.Atom('zigzag'), bad):
            with self.assertRaises(K.Refusal) as e:
                self.send(m, w, 'draw_filled_rectangle', 0, 0, 5, 5, 0, pt, K.Atom('set'))
            self.assertIn('graphics_refused', str(e.exception.detail))
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual(set(fr.status), {winfb.OK})
        self.assertEqual(winfb.run_stream(windev.device(m).stream_text()).pbm(), fr.pbm())

    def image_ref(self, want, codes, x, y, wd, ht):
        # the reference restore_image/6: WD x HT dots at inside (X, Y),
        # ceil(WD/16) words a row, MSB leftmost, opaque
        X0, Y0 = self.GRAPHICS_AT
        n = (wd + 15) // 16
        for j in range(ht):
            for i in range(wd):
                bit = 1 << (1279 - X0 - x - i)
                if (codes[j * n + i // 16] >> (15 - i % 16)) & 1:
                    want.rows[Y0 + y + j] |= bit
                else:
                    want.rows[Y0 + y + j] &= ~bit

    def test_win_m8_images(self):
        # M8's rest, images (window.md §2.5; standard_io_window.esp
        # "IMAGES", window_pane.esp image_in/6, bitmap.esp):
        #   - :get_plane_count(#bitmap, N) is 1, so the HELD
        #     profiler_icon_image_lib's class slot `color` (initialised by
        #     its color_check2/1) is 1, the monochrome path;
        #   - light_paint MEASURED: the HELD profiler_mono_selector_image
        #     (p_v_imag.esp:151-152, :228: fix set, light_paint reset, saved
        #     at the inside's (0, 0)) has 16#"7777" only on even rows and
        #     16#"DDDD" only on odd ones, the complement of window_pane.esp's
        #     light_paint (8888, 2222);
        #   - restore_image/6 of the HELD profiler_icon_image3 (16 x 112)
        #     over a black block: opaque, equal to the reference; twice,
        #     the same frame;
        #   - the HELD paragraph##type_switch_icon :draw/6 (p_icon.esp:170
        #     -186: three draw_box/5 and :restore(#profiler_icon_image_lib,
        #     Win, image1, X+1, Y+24, 16, h1), whose restore/7 adjusts Y by
        #     get_label_height/2 - 24 and sends restore_image/6) equals the
        #     three held draw_box/5 and the reference image1 at (X+1, Y+24
        #     + 16 - 24); get_label_height/2 is 16;
        #   - refused loudly: an image leaving the inside, a string too
        #     short for its size; the frame unchanged.
        # Injections, OBSERVED (2026-11-26; each from a backup copy,
        # restored by copy, cmp clean; Window, test_fep_bridge.py and
        # test_kl0.py run, all else OK; rerun at the final code with the
        # Window tests, the results below):
        #   G13 image_in/6 draws transparent (no reset of the area): this
        #       test and test_win_m8_rest_screen FAIL, nothing else.
        #   G14 get_plane_count/2 answers 3: this test FAILS and
        #       test_win_m8_rest_screen ERRORS, nothing else.
        import windev
        import winfb
        X0, Y0 = self.GRAPHICS_AT
        m, w = self.graphics_window()
        fr = windev.device(m).frame
        self.assertEqual(K.call_class_method(m, 'simpos##bitmap', 'get_plane_count', [K.Var()]), [[1]])
        self.assertEqual(m.get_slot(K.ClassRef('paragraph##profiler_icon_image_lib'), 'color'), 1)

        def image(cid):
            ((s,),) = K.call_class_method(m, cid, 'get', [K.Var()])
            return s.codes()
        sel = image('paragraph##profiler_mono_selector_image')
        self.assertEqual(len(sel), 24 * 238)
        rows = {0x7777: set(), 0xDDDD: set()}
        for i, c in enumerate(sel):
            if c in rows:
                rows[c].add((i // 24) % 2)
        self.assertEqual(rows, {0x7777: {0}, 0xDDDD: {1}})
        lp = self.NAMED_PATTERNS['light_paint']
        self.assertEqual([0xffff & ~0x7777, 0xffff & ~0xDDDD], lp[:2])
        # restore_image/6, opaque over black
        img3 = image('paragraph##profiler_icon_image3')
        self.assertEqual(len(img3), 112)
        self.assertTrue(self.send(m, w, 'draw_filled_rectangle', 0, 0, 40, 130, K.Atom('set')))
        want = winfb.Frame()
        want.rows = list(fr.rows)
        ((s3,),) = K.call_class_method(m, 'paragraph##profiler_icon_image3', 'get', [K.Var()])
        self.assertTrue(self.send(m, w, 'restore_image', s3, 10, 10, 16, 112))
        self.image_ref(want, img3, 10, 10, 16, 112)
        self.assertEqual(fr.rows, want.rows)
        self.assertTrue(self.send(m, w, 'restore_image', s3, 10, 10, 16, 112))
        self.assertEqual(fr.rows, want.rows)
        # the held icon's draw/6, against its own draw_box/5 and the image
        lh = K.Var()
        self.assertTrue(self.send(m, w, 'get_label_height', lh))
        self.assertEqual(K.resolve(lh), 16)
        ic = K.make_instance(m, 'paragraph##type_switch_icon')
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(ic, 'draw', [100, 20, 20, 84, w, ic])))
        m2, w2 = self.graphics_window()
        self.assertTrue(self.send(m2, w2, 'draw_filled_rectangle', 0, 0, 40, 130, K.Atom('set')))
        self.assertTrue(self.send(m2, w2, 'restore_image', s3, 10, 10, 16, 112))
        for k in range(3):
            self.assertEqual(self.held_draw_box(m2, w2, 100, 20 + 28 * k, 19, 28), 1)
        ref = winfb.Frame()
        ref.rows = list(windev.device(m2).frame.rows)
        self.image_ref(ref, image('paragraph##profiler_icon_image1'), 101, 20 + 24 + 16 - 24, 16, 84)
        self.assertEqual(fr.rows, ref.rows)
        # refusals
        rows = list(fr.rows)
        for args in ((s3, 430, 10, 16, 112), (s3, 10, 10, 16, 113)):
            with self.assertRaises(K.Refusal) as e:
                self.send(m, w, 'restore_image', *args)
            self.assertIn('graphics_refused', str(e.exception.detail))
        self.assertEqual(fr.rows, rows)
        self.assertEqual(set(fr.status), {winfb.OK})
        self.assertEqual(winfb.run_stream(windev.device(m).stream_text()).pbm(), fr.pbm())

    # window M8's rest, shapes: the reference dots of window_pane.esp
    # shape_in/9 (OURS rules, its header), repeated here dot by dot
    SINE = [0, 18, 36, 54, 71, 89, 107, 125, 143, 160, 178, 195, 213, 230, 248, 265, 282, 299,
            316, 333, 350, 367, 384, 400, 416, 433, 449, 465, 481, 496, 512, 527, 543, 558, 573,
            587, 602, 616, 630, 644, 658, 672, 685, 698, 711, 724, 737, 749, 761, 773, 784, 796,
            807, 818, 828, 839, 849, 859, 868, 878, 887, 896, 904, 912, 920, 928, 935, 943, 949,
            956, 962, 968, 974, 979, 984, 989, 994, 998, 1002, 1005, 1008, 1011, 1014, 1016,
            1018, 1020, 1022, 1023, 1023, 1024, 1024]

    def unit(self, d):
        q, r = divmod(d % 360, 90)
        sr, cr = self.SINE[r], self.SINE[90 - r]
        return [(cr, sr), (-sr, cr), (-cr, -sr), (sr, -cr)][q]

    def shape_dots(self, rx, ry, wd, angles=None):
        # the dots (dx, dy) from the centre (dy down) of shape_in/9
        def h(r, y):
            x = r
            while x * x > r * r + r - y * y:
                x -= 1
            return x

        def half(a, b, hh):
            return a if b == 0 else a * hh // b
        ri = ry - wd
        sec = None
        if angles and angles[0] % 360 != angles[1] % 360:
            sec = (self.unit(angles[0]), self.unit(angles[1]),
                   (angles[1] - angles[0]) % 360 > 180)
        dots = set()
        for y in range(ry + 1):
            a = half(rx, ry, h(ry, y))
            b = None
            if wd > 0 and ri >= 0 and rx - wd >= 0 and y <= ri:
                b = half(rx - wd, ri, h(ri, y))
            for u in ([y] if y == 0 else [y, -y]):
                for x in range(-a, a + 1):
                    if b is not None and abs(x) <= b:
                        continue
                    if sec:
                        (c1, s1), (c2, s2), wide = sec
                        i1, i2 = c1 * u - s1 * x >= 0, c2 * u - s2 * x <= 0
                        if not ((i1 or i2) if wide else (i1 and i2)):
                            continue
                    dots.add((x, -u))
        return dots

    def rim(self, cx, cy, r, a):
        c, s = self.unit(a)
        return cx + (r * c + 512) // 1024, cy - (r * s + 512) // 1024

    def put_dots(self, want, cx, cy, dots, pattern=None, iw=440, ih=280):
        X0, Y0 = self.GRAPHICS_AT
        for dx, dy in dots:
            x, y = cx + dx, cy + dy
            if 0 <= x < iw and 0 <= y < ih and (pattern is None or self.pattern_dot(pattern, x, y)):
                want.rows[Y0 + y] |= 1 << (1279 - X0 - x)

    def put_line(self, want, x1, y1, x2, y2, wd, op=0):
        # draw_line_in/7's line, op OP (0 set, 2 exclusive_or): a fill when level or upright, else
        # the device line (windev line/7, style all ones)
        import winfb
        X0, Y0 = self.GRAPHICS_AT
        if y1 == y2:
            want.command(winfb.FILL << 4 | op, [X0 + min(x1, x2), Y0 + y1, abs(x2 - x1) + 1, wd, 0, 0])
        elif x1 == x2:
            want.command(winfb.FILL << 4 | op, [X0 + x1, Y0 + min(y1, y2), wd, abs(y2 - y1) + 1, 0, 0])
        else:
            want.command(winfb.LINE << 4 | op, [X0 + x1, Y0 + y1, X0 + x2, Y0 + y2, wd, 0xffff])

    def test_win_m8_shapes(self):
        # M8's rest, shapes (window.md §2.5; standard_io_window.esp
        # "SHAPES", window_pane.esp shape_in/9, fan_in/8, lines_in/5):
        # the selectors and argument orders PRINTED WINCS p3 and
        # PRINTED-INTERFACE TM-785 p40, the dots OURS, each drawing checked
        # against shape_dots/4 (the rules repeated dot by dot) or the winfb
        # commands of its lines:
        #   - draw_circle/7 (the HELD kappa make_copyright/2 arguments,
        #     MOPMANAGER.ESP:154 `(Window,16,22,10,1,solid,set)`, and a
        #     3-dot outline), draw_filled_circle/5, draw_ellipse/8,
        #     draw_filled_ellipse/7 cut to the inside;
        #   - draw_arc/9 280 to 40 (through 0: the TM-785 p40 angles),
        #     draw_elliptical_arc/10 95 to 170, draw_filled_fan/9 30 to 300
        #     (a sweep of 270, wider than 180);
        #   - draw_fan/9: the arc and its two slanted radii;
        #   - draw_filled_circle/7 with light_paint (pattern_dot/4's dots);
        #   - draw_graph/2 (the held kwic scrolls.esp:1135 form: a list of
        #     (X, Y)) open, draw_polygon/9 closed;
        #   - execute_graphics_command/2 with TM-785 p40's vectors
        #     draw_circle {CX, CY, R, W, St, Op} and draw_arc;
        #   - exclusive_or twice erases a filled fan and an arc;
        #   - refused loudly, the frame unchanged: style dotted, an integer
        #     (colour) op, a negative angle, width 0, a polygon leaving the
        #     inside, a fan whose radius leaves it, an unknown pattern.
        # Injections, OBSERVED (2026-11-26; each from a backup copy,
        # restored by copy, cmp clean; Window, test_fep_bridge.py and
        # test_kl0.py run, all else OK; rerun at the final code with the
        # Window tests, the results below):
        #   G15 the disc rule x*x + y*y =< R*R (no + R): this test and
        #       test_win_m8_rest_screen FAIL, nothing else.
        #   G16 a sweep over 180 degrees taken as narrow: this test and
        #       test_win_m8_rest_screen FAIL, nothing else.
        #   G17 no inner ellipse (every outline filled): this test and
        #       test_win_m8_rest_screen FAIL, nothing else.
        #   G18 the polygon not closed: this test and
        #       test_win_m8_rest_screen FAIL, nothing else.
        #   G19 draw_fan/9 without its first radius: this test FAILS,
        #       nothing else.
        #   G20 an outline's op not checked (an integer colour op sent on):
        #       this test FAILS, nothing else.
        #   G21 the second quadrant's cosine not negated: this test FAILS,
        #       nothing else.
        #   E3 TM-785 p40's six-element draw_filled_ellipse vector drawn
        #      (read as {CX, CY, RX, RY, Pattern, Op}), not refused: this
        #      test FAILS, nothing else (test_fep_bridge.py,
        #      test_kl0.py also run: OK).
        import windev
        import winfb
        A = K.Atom
        m, w = self.graphics_window()
        fr = windev.device(m).frame
        want = winfb.Frame()
        want.rows = list(fr.rows)
        S, SET = A('solid'), A('set')

        def drawn(sel, *args):
            self.assertTrue(self.send(m, w, sel, *args), sel)
            self.assertEqual(fr.rows, want.rows, sel)
        self.put_dots(want, 16, 22, self.shape_dots(10, 10, 1))
        drawn('draw_circle', 16, 22, 10, 1, S, SET)
        self.put_dots(want, 60, 60, self.shape_dots(40, 40, 3))
        drawn('draw_circle', 60, 60, 40, 3, S, SET)
        self.put_dots(want, 160, 60, self.shape_dots(30, 30, 0))
        drawn('draw_filled_circle', 160, 60, 30, SET)
        self.put_dots(want, 300, 60, self.shape_dots(60, 25, 2))
        drawn('draw_ellipse', 300, 60, 60, 25, 2, S, SET)
        self.put_dots(want, 420, 260, self.shape_dots(40, 30, 0))
        drawn('draw_filled_ellipse', 420, 260, 40, 30, A('fix'), SET)
        self.put_dots(want, 60, 180, self.shape_dots(50, 50, 4, (280, 40)))
        drawn('draw_arc', 60, 180, 50, 280, 40, 4, S, SET)
        self.put_dots(want, 200, 180, self.shape_dots(60, 30, 3, (95, 170)))
        drawn('draw_elliptical_arc', 200, 180, 60, 30, 95, 170, 3, S, SET)
        self.put_dots(want, 340, 200, self.shape_dots(50, 50, 0, (30, 300)))
        drawn('draw_filled_fan', 340, 200, 50, 30, 300, 1, A('fix'), SET)
        # draw_fan/9: the arc, then the radii (slanted at 20 and 130)
        self.put_dots(want, 120, 240, self.shape_dots(30, 30, 1, (20, 130)))
        for a in (20, 130):
            x, y = self.rim(120, 240, 30, a)
            self.put_line(want, 120, 240, x, y, 1)
        drawn('draw_fan', 120, 240, 30, 20, 130, 1, S, SET)
        lp = A('light_paint')
        self.put_dots(want, 250, 250, self.shape_dots(25, 25, 0), lp)
        drawn('draw_filled_circle', 250, 250, 25, 1, lp, SET)
        # polylines: the graph open, the polygon closed
        pts = [(380, 100), (430, 100), (430, 140), (390, 130)]

        def plist(ps):
            out = K.NIL
            for x, y in reversed(ps):
                out = K.Cons(K.Vec([A(','), x, y]), out)
            return out
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            self.put_line(want, x1, y1, x2, y2, 1, 2)     # exclusive_or: the shared ends cancel
        drawn('draw_graph', plist(pts))
        tri = [(10, 100), (40, 100), (25, 130)]
        for (x1, y1), (x2, y2) in zip(tri, tri[1:] + tri[:1]):
            self.put_line(want, x1, y1, x2, y2, 2)
        drawn('draw_polygon', plist(tri), 0, 0, 400, 400, 2, S, SET)
        # execute_graphics_command/2 with TM-785 p40's vectors
        self.put_dots(want, 420, 20, self.shape_dots(15, 15, 1))
        self.put_dots(want, 420, 20, self.shape_dots(10, 10, 2, (280, 40)))
        cmds = K.Cons(K.Vec([A('draw_circle'), K.Vec([420, 20, 15, 1, S, SET])]),
                      K.Cons(K.Vec([A('draw_arc'), K.Vec([420, 20, 10, 280, 40, 2, S, SET])]), K.NIL))
        drawn('execute_graphics_command', cmds)
        # exclusive_or: once each dot, twice none
        rows = list(fr.rows)
        X = A('exclusive_or')
        self.assertTrue(self.send(m, w, 'draw_filled_fan', 200, 120, 20, 300, 60, 1, A('fix'), X))
        self.assertNotEqual(fr.rows, rows)
        self.assertTrue(self.send(m, w, 'draw_filled_fan', 200, 120, 20, 300, 60, 1, A('fix'), X))
        self.assertTrue(self.send(m, w, 'draw_arc', 60, 60, 40, 0, 180, 2, S, X))
        self.assertTrue(self.send(m, w, 'draw_arc', 60, 60, 40, 0, 180, 2, S, X))
        self.assertEqual(fr.rows, rows)
        for args in [('draw_circle', 100, 100, 10, 1, A('dotted'), SET),
                     ('draw_circle', 100, 100, 10, 1, S, 1),
                     ('draw_arc', 100, 100, 10, 0, -1, 1, S, SET),
                     ('draw_ellipse', 100, 100, 10, 5, 0, S, SET),
                     ('draw_polygon', plist([(10, 10), (450, 20), (10, 30)]), 0, 0, 0, 0, 1, S, SET),
                     ('draw_fan', 100, 20, 40, 60, 120, 1, S, SET),
                     ('draw_filled_circle', 100, 100, 10, 1, A('zigzag'), SET),
                     # TM-785 p40's six-element draw_filled_ellipse vector,
                     # ambiguous (standard_io_window.esp command/4)
                     ('execute_graphics_command',
                      K.Cons(K.Vec([A('draw_filled_ellipse'), K.Vec([200, 50, 100, 1, A('fix'), SET])]), K.NIL))]:
            with self.assertRaises(K.Refusal) as e:
                self.send(m, w, *args)
            self.assertIn('graphics_refused', str(e.exception.detail))
        self.assertEqual(fr.rows, rows)
        self.assertEqual(set(fr.status), {winfb.OK})
        self.assertEqual(winfb.run_stream(windev.device(m).stream_text()).pbm(), fr.pbm())

    def block(self, fr, x, y, w, h):
        # the dots of the screen rectangle, row by row
        return [(fr.rows[y + j] >> (1280 - x - w)) & ((1 << w) - 1) for j in range(h)]

    def test_win_m8_copy(self):
        # M8's rest, copy/9 between windows (window.md §2.5; USAGE icotext
        # util_scroll.esp:211 `(W, Src, SX, SY, DX, DY, Width, Height, Op)`,
        # the direction INFERENCE; window_pane.esp copy_in/9, OURS):
        #   - a 60 x 40 block of the graphics window (a filled circle and a
        #     line) copied into a second window at (20, 20) of its inside
        #     (exclusive_or onto the empty block): the block's dots there,
        #     the rest of both windows unchanged;
        #   - copied again with exclusive_or: the second window's block
        #     cleared (dots XOR themselves), the frame as before;
        #   - with copy into the second window while a third covers part
        #     of it: the third's dots unchanged, and once the second is
        #     selected (raised) its block shows the source's dots;
        #   - with exclusive_or while a fourth window covers part of the
        #     source: the fourth's dots unchanged, the copy cleared;
        #   - refused loudly, the frame unchanged: the other held form
        #     (an integer second argument: util_scroll.esp:218's matrix
        #     copy), a source not shown (util_scroll's hide_window), an
        #     area leaving the inside, a colour (integer) op.
        # paint/5 (USAGE kappa2 pdim.esp:606) is refused loudly too: a STOP
        # (standard_io_window.esp "PAINT": a seed fill needs the frame's
        # dots, which no frozen primitive gives the program).
        # Injections, OBSERVED (2026-11-26; each from a backup copy,
        # restored by copy, cmp clean; Window, test_fep_bridge.py and
        # test_kl0.py run, all else OK; rerun at the final code with the
        # Window tests, the results below):
        #   C1 copy_in/9 does not draw the destination's own dots back (D)
        #      before the copy goes on through Op: this test FAILS, nothing
        #      else.  (First run, with the first copy `copy` onto the empty
        #      block: NOTHING failed, since D does not matter to `copy`;
        #      the first copy is exclusive_or since.)
        #   C2 the copy drawn `copy` whatever Op: this test FAILS, nothing
        #      else.
        #   C3 the screen under the source's block (B) not drawn back: this
        #      test FAILS, nothing else.
        #   C4 the source saved without uncover/3 (its covers' dots
        #      copied): this test FAILS, nothing else.
        import windev
        import winfb
        A = K.Atom
        X0, Y0 = self.GRAPHICS_AT
        m, w = self.graphics_window()
        fr = windev.device(m).frame

        def made(x, y, cols, rows):
            opts = K.Cons(K.Vec([A('position'), x, y]),
                          K.Cons(K.Vec([A('size'), K.Vec([A('ch'), cols]), K.Vec([A('ch'), rows])]), K.NIL))
            ((_o, v),) = K.call_class_method(m, 'simpos##standard_io_window', 'create', [opts, K.Var()])
            self.assertTrue(self.send(m, v, 'activate'))
            return v
        self.assertTrue(self.send(m, w, 'draw_filled_circle', 30, 20, 15, A('set')))
        self.assertTrue(self.send(m, w, 'draw_line', 0, 0, 59, 39, 1, A('solid'), A('set')))
        src = self.block(fr, X0 + 0, Y0 + 0, 60, 40)
        self.assertGreater(sum(bin(r).count('1') for r in src), 700)
        w2 = made(700, 100, 20, 10)
        P2 = m.get_slot(w2, 'pane')
        L2, T2 = m.get_slot(P2, 'left'), m.get_slot(P2, 'top')
        before = list(fr.rows)
        self.assertTrue(self.send(m, w2, 'copy', w, 0, 0, 20, 20, 60, 40, A('exclusive_or')))
        self.assertEqual(self.block(fr, L2 + 20, T2 + 20, 60, 40), src)
        want = winfb.Frame()
        want.rows = list(before)
        for j, r in enumerate(src):
            y = T2 + 20 + j
            want.rows[y] = want.rows[y] & ~(((1 << 60) - 1) << (1280 - L2 - 20 - 60)) | (r << (1280 - L2 - 20 - 60))
        self.assertEqual(fr.rows, want.rows)
        self.assertTrue(self.send(m, w2, 'copy', w, 0, 0, 20, 20, 60, 40, A('exclusive_or')))
        self.assertEqual(self.block(fr, L2 + 20, T2 + 20, 60, 40), [0] * 40)
        self.assertEqual(fr.rows, before)
        # a third window over part of the second
        w3 = made(760, 130, 10, 4)
        P3 = m.get_slot(w3, 'pane')
        x3, y3, wd3, ht3 = (m.get_slot(P3, k) for k in ('x', 'y', 'w', 'h'))
        over = self.block(fr, x3, y3, wd3, ht3)
        self.assertTrue(self.send(m, w2, 'copy', w, 0, 0, 20, 20, 60, 40, A('copy')))
        self.assertEqual(self.block(fr, x3, y3, wd3, ht3), over)
        self.assertNotEqual(self.block(fr, L2 + 20, T2 + 20, 60, 40), src)
        K.call_class_method(m, 'simpos##coordinator', 'select_window', [w2])
        self.assertEqual(self.block(fr, L2 + 20, T2 + 20, 60, 40), src)
        # a fourth window over part of the source block: copied with
        # exclusive_or onto its own copy, the second window's block clears,
        # the fourth's dots unchanged
        w4 = made(130, 125, 6, 2)
        P4 = m.get_slot(w4, 'pane')
        x4, y4, wd4, ht4 = (m.get_slot(P4, k) for k in ('x', 'y', 'w', 'h'))
        over = self.block(fr, x4, y4, wd4, ht4)
        self.assertTrue(self.send(m, w2, 'copy', w, 0, 0, 20, 20, 60, 40, A('exclusive_or')))
        self.assertEqual(self.block(fr, x4, y4, wd4, ht4), over)
        self.assertEqual(self.block(fr, L2 + 20, T2 + 20, 60, 40), [0] * 40)
        rows = list(fr.rows)
        (_o, hidden), = K.call_class_method(m, 'simpos##standard_io_window', 'create', [K.NIL, K.Var()])
        for args in [('copy', 0, 0, w, 0, 0, 60, 40, K.Vec([2, 0, 0, 0, 2, 0])),
                     ('copy', hidden, 0, 0, 20, 20, 60, 40, A('copy')),
                     ('copy', w, 0, 0, 200, 20, 60, 40, A('copy')),
                     ('copy', w, 0, 0, 20, 20, 60, 40, 1),
                     ('paint', 1, 1, A('light_paint'), A('set'))]:
            with self.assertRaises(K.Refusal) as e:
                self.send(m, w2, *args)
            self.assertIn('graphics_refused', str(e.exception.detail))
        self.assertEqual(fr.rows, rows)
        self.assertEqual(set(fr.status), {winfb.OK})
        self.assertEqual(winfb.run_stream(windev.device(m).stream_text()).pbm(), fr.pbm())

    def graphics_rest_run(self):
        # the screen of psi/winshot.py's `graphics_rest` stage (window M8's
        # rest): in the 40 x 20 graphics window, the HELD g_window bar
        # views (draw_list_b/8 with the held set_pattern/2 strings), the
        # HELD type_switch_icon draw/6 (boxes and its image), and the
        # shapes: a circle outline, an arc, a light_paint fan, a filled
        # ellipse, a polygon.  -> (machine, frame)
        import windev
        A = K.Atom
        m, w = self.graphics_window()
        pats = self.held_patterns(m)
        cid = 'paragraph##g_window'
        ps = {(p.name, p.arity): p for p in m.lib.templates[cid].locals}
        ((_n, font),) = K.call_class_method(m, 'simpos##font', 'create', [K.Str('font:test_11.font'), K.Var()])
        items = K.NIL
        for i in reversed(range(6)):
            items = K.Cons(pats[i], K.Cons(i + 1, items))
        m.reset()
        dl = K.Var()
        (dl,) = [K.resolve(dl) for _ in m.solve((m.code(cid), ps[('draw_list_b', 8)].offset),
                                                [10, 10, 1, items, dl, font, 30, 280])]
        self.assertTrue(self.send(m, w, 'execute_graphics_command', dl))
        ic = K.make_instance(m, 'paragraph##type_switch_icon')
        m.reset()
        self.assertTrue(any(True for _ in m.solve_send(ic, 'draw', [300, 20, 20, 84, w, ic])))
        S, SET = A('solid'), A('set')
        self.assertTrue(self.send(m, w, 'draw_circle', 380, 60, 40, 2, S, SET))
        self.assertTrue(self.send(m, w, 'draw_arc', 380, 60, 28, 280, 40, 3, S, SET))
        self.assertTrue(self.send(m, w, 'draw_filled_fan', 360, 200, 50, 30, 300, 1, A('light_paint'), SET))
        self.assertTrue(self.send(m, w, 'draw_filled_ellipse', 250, 230, 40, 20, A('fix'), SET))
        pts = K.NIL
        for x, y in reversed([(220, 130), (290, 130), (255, 180)]):
            pts = K.Cons(K.Vec([A(','), x, y]), pts)
        self.assertTrue(self.send(m, w, 'draw_polygon', pts, 0, 0, 400, 400, 2, S, SET))
        return m, windev.device(m).frame

    def test_win_m8_rest_screen(self):
        # the pinned frame of graphics_rest_run (psi/winshot.py
        # `graphics_rest`, docs/simpos/screens/window_graphics_rest.png)
        import windev
        m, fr = self.graphics_rest_run()
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.GRAPHICS_REST_PIN)

    GRAPHICS_REST_PIN = ('54cf1490c64bc06f167057ab9c5800652588eece19c56c45f5a861f695ca1512', 110989)

    def choice_run(self):
        # the screen of psi/winshot.py's `choice` stage (window M9): the
        # HELD pimfep superviser's error mode menu (error_mode_menu/2 on
        # the .ptf), error_mode set on, at (300, 200), activated, after the
        # Login PIMOS run.  -> (machine, frame, menu)
        import windev
        m, fr, _ = self.later_run(self.manip_events()['login'])
        m.reset()
        sup = K.make_instance(m, 'pimfep##pimos_fep_superviser')
        v = K.Var()
        self.assertTrue(self.send(m, sup, 'error_mode_menu', v))
        menu = K.resolve(v)
        self.assertTrue(self.send(m, menu, 'set_item_value', K.Atom('error_mode'), K.Atom('on')))
        self.assertTrue(self.send(m, menu, 'set_position', 300, 200))
        self.assertTrue(self.send(m, menu, 'activate'))
        return m, fr, menu

    CHOICE_PIN = ('0633597d7e5c582173f43f37130de60beea360634ad5fe5bbf6a61940374eb5e', 103105)

    def test_win_m9_choice_screen(self):
        # the pinned frame of choice_run (psi/winshot.py `choice`,
        # docs/simpos/screens/choice_window.png); the committed PNGs
        # decode to their pins (assert_shots)
        import windev
        m, fr, _menu = self.choice_run()
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.CHOICE_PIN)
        self.assert_shots()

    # the error mode menu's outer size: 15 x 5 cells of the default font
    # (11 x 14 dots), window_pane.esp's layout (OURS)
    CHOICE_SIZE = (171, 93)

    def test_win_m9_attribute(self):
        # M9, the manipulator's ATTRIBUTE (TM-125 p8; Fig. 4's sheet;
        # coordinator.esp manipulate/3, choice_done/3): in the run of two
        # requester windows, the manipulator opened on window 2 and its
        # ATTRIBUTE item clicked: a choice window at the mouse, owned by
        # the coordinator, its PERMISSION field (OURS: Fig. 4's one field
        # the stand-ins keep) showing window 2's own `out` reversed.
        # `wait` clicked, then do_it: window 2's permission is wait, the
        # sheet is gone, and the frame is the run's before the
        # manipulator (the selected window's cursor back).  `wait`, then
        # abort: the permission stays out.  The events are the run's own
        # (later_run batches through the coordinator's stream).
        # Injections, OBSERVED: see test_win_m9_choice's header (M1-M4,
        # A1, E1, E2).
        E = self.manip_events()
        C = K.ClassRef('simpos##coordinator')
        login, two = E['login'], E['two']
        m, base, _ = self.later_run(login, two)
        m, sheet, _ = self.later_run(login, two, E['attribute'])
        M = K.resolve(m.get_slot(C, 'sheet'))
        (w2, s), = [self._walk(M)]
        self.assertEqual(s.cid, 'simpos##standard_choice_window')
        self.assertEqual(self._walk(m.get_slot(C, 'choices')), [s])
        P = m.get_slot(s, 'pane')
        self.assertEqual([m.get_slot(P, k) for k in ('x', 'y', 'left', 'top')], [700, 700, 703, 720])
        import windev
        self.assertEqual(windev.read_cells(sheet, 703, 720, 16, 1), ['WINDOW ATTRIBUTE'])
        self.assertEqual(windev.read_cells(sheet, 703 + 15 * 11, 734, 4, 1), ['wait'])
        self.assertEqual((windev.pbm_sha256(sheet), sheet.count()), self.SHOT_PINS['attribute'])
        # the sheet is owned by the coordinator's own process, so its
        # writes go through manager/1's bypass in this run
        owners = [self._walk(o) for o in self._walk(m.get_slot(C, 'owners'))]
        self.assertIn([s, K.deref(m.get_slot(C, 'process'))], owners)
        self.assertNotEqual(K.deref(m.get_slot(C, 'process')), 0)
        # the sheet is not a window the user arranges: a middle click on
        # it opens no manipulator, and MENU's submenu does not list it
        import fep_bridge as FB
        m, mid, _ = self.later_run(login, two, E['attribute'], [FB.mouse('m', 720, 740)])
        self.assertEqual(K.deref(m.get_slot(C, 'menu_pane')), 0)
        self.assertEqual(mid.rows, sheet.rows)
        m, _, _ = self.later_run(login, two, E['attribute'], E['windows'])
        Mp = K.deref(m.get_slot(C, 'menu_pane'))
        listed = [K.deref(K.deref(i).args[1]) for col in self._walk(m.get_slot(Mp, 'columns'))
                  for i in self._walk(col)]
        S2 = self._walk(m.get_slot(C, 'choices'))
        self.assertEqual(len(listed), 2)
        self.assertEqual(len(S2), 1)
        self.assertNotIn(S2[0], listed)
        m, done, _ = self.later_run(login, two, E['attribute'], E['attribute_wait'], E['attribute_do_it'])
        w2 = self.manip_check(m, done, [self.MANIP_W2, self.MANIP_W1])[0]
        self.assertEqual(m.get_slot(w2, 'permission'), K.Atom('wait'))
        self.assertEqual((m.get_slot(C, 'sheet'), self._walk(m.get_slot(C, 'choices'))), (K.NIL, []))
        self.assertEqual(done.rows, base.rows)
        m, kept, _ = self.later_run(login, two, E['attribute'], E['attribute_wait'], E['attribute_abort'])
        w2 = self.manip_check(m, kept, [self.MANIP_W2, self.MANIP_W1])[0]
        self.assertEqual(m.get_slot(w2, 'permission'), K.Atom('out'))
        self.assertEqual(kept.rows, base.rows)

    def test_win_m9_choice(self):
        # M9, the choice window (window.md §2.10, §3.4;
        # standard_choice_window.esp): the HELD pimfep superviser's error
        # mode menu.  After the Login PIMOS run, a pimos_fep_superviser
        # instance's held error_mode_menu/2 (the .ptf: it runs the held
        # local create_error_mode_menu/1 @48a, whose create/3 carries the
        # choice_list and label_flag(off)) gives the menu; then
        # refute_sub_command/2 @36c-3b0's sends (OURS harness: the sends
        # copied, the FEP object's own steps left out): set_item_value/3
        # error_mode on, get_size/3, set_position/3, activate/1:
        #   - the sheet: "   ERROR Mode", then the choose row with `on`
        #     reversed (OURS look), the button row " do_it  abort ";
        #   - a left click on `off` (the coordinator's event/2) reverses
        #     `off` instead, and the coordinator selects nothing;
        #   - a click on do_it, then read/2: [{error_mode, off}], the
        #     held `R = [{error_mode, V}]` shape;
        #   - deactivate/1: the frame as before activate/1 (the selected
        #     window's cursor back), no window or choice left in the
        #     coordinator;
        #   - activated again, `on` clicked (away from the held default
        #     off), do_it: [{error_mode, on}]; then abort clicked: read/2
        #     gives abort;
        #   - set_item_value/3 on a key the menu lacks refuses loudly.
        # Injections, OBSERVED (2026-11-26; each from a backup copy,
        # restored by copy, cmp clean; Window, test_fep_bridge.py and
        # test_kl0.py run, all else OK; rerun at the final code with the
        # Window tests, the results below):
        #   M1 a click on an option does not change the field's value:
        #      this test and test_win_m9_attribute FAIL, nothing else.
        #   M2 the coordinator sends a click on a choice window to a
        #      selection (no choose/3): this test ERRORS and
        #      test_win_m9_attribute FAILS, nothing else.
        #   M3 deactivate/1 does not give the selected window its cursor
        #      back: this test and test_win_m9_attribute FAIL, nothing
        #      else.
        #   M4 read/2 returns the fields' defaults, not their values (the
        #      plan's injection): first run, NOTHING failed (the one edit
        #      ended on the held default, off); with the edit to `on`
        #      added, this test and test_win_m9_attribute FAIL, nothing
        #      else.
        #   A1 ATTRIBUTE's do_it sets nothing (attribute_set/2 ignores the
        #      result): test_win_m9_attribute FAILS, nothing else.
        #   E1 a middle click on a choice window opens the manipulator on
        #      it (no not_choice/2): test_win_m9_attribute FAILS, nothing
        #      else (test_fep_bridge.py,
        #      test_kl0.py also run: OK).
        #   E2 MENU's listed/3 lists the choice windows:
        #      test_win_m9_attribute FAILS, nothing else
        #      (test_fep_bridge.py, test_kl0.py also run: OK).
        import fep_bridge as FB
        import windev
        A = K.Atom
        m, fr, _ = self.later_run(self.manip_events()['login'])
        m.reset()
        C = K.ClassRef('simpos##coordinator')
        sup = K.make_instance(m, 'pimfep##pimos_fep_superviser')
        v = K.Var()
        self.assertTrue(self.send(m, sup, 'error_mode_menu', v))
        menu = K.resolve(v)
        self.assertEqual(menu.cid, 'simpos##standard_choice_window')
        self.assertTrue(self.send(m, menu, 'set_item_value', A('error_mode'), A('on')))
        wv, hv = K.Var(), K.Var()
        self.assertTrue(self.send(m, menu, 'get_size', wv, hv))
        self.assertEqual((K.resolve(wv), K.resolve(hv)), self.CHOICE_SIZE)
        self.assertTrue(self.send(m, menu, 'set_position', 300, 200))
        before = list(fr.rows)
        self.assertTrue(self.send(m, menu, 'activate'))
        pane = m.get_slot(menu, 'pane')
        left, top, cw, ch = (m.get_slot(pane, k) for k in ('left', 'top', 'cw', 'ch'))

        def row(r, c0, n, inverted=()):
            # row R's cells C0.. read back, the INVERTED cells first
            # inverted again in a copy of the frame
            import winfb
            f = winfb.Frame()
            f.rows = list(fr.rows)
            for c, k in inverted:
                f.command(winfb.FILL << 4 | 2, [left + c * cw, top + r * ch, k * cw, ch, 0, 0])
            return windev.read_cells(f, left + c0 * cw, top + r * ch, n, 1)[0]
        self.assertEqual(row(0, 0, 13), '   ERROR Mode')
        self.assertEqual(row(2, 0, 11, [(5, 2)]), '     on off')
        self.assertNotEqual(row(2, 5, 2), 'on')
        self.assertEqual(row(4, 0, 14), ' do_it  abort')     # read_cells drops the trailing space

        def click(c, r):
            K.call_class_method(m, 'simpos##coordinator', 'event',
                                [FB.mouse('l', left + c * cw + cw // 2, top + r * ch + ch // 2)])
        selected = m.get_slot(C, 'selected')
        click(9, 2)
        self.assertEqual(row(2, 0, 11, [(8, 3)]), '     on off')
        self.assertEqual(row(2, 5, 2), 'on')
        self.assertIs(m.get_slot(C, 'selected'), selected)
        click(2, 4)
        r = K.Var()
        self.assertTrue(self.send(m, menu, 'read', r))
        self.assertEqual(repr(K.resolve(r)), repr(K.Cons(K.Vec([A('error_mode'), A('off')]), K.NIL)))
        self.assertTrue(self.send(m, menu, 'deactivate'))
        self.assertEqual(fr.rows, before)
        self.assertNotIn(menu, self._walk(m.get_slot(C, 'windows')))
        self.assertEqual(self._walk(m.get_slot(C, 'choices')), [])
        self.assertTrue(self.send(m, menu, 'activate'))
        # the field edited away from its default (the held default is
        # off): `on` clicked, then do_it
        click(6, 2)
        self.assertEqual(row(2, 0, 11, [(5, 2)]), '     on off')
        click(2, 4)
        r = K.Var()
        self.assertTrue(self.send(m, menu, 'read', r))
        self.assertEqual(repr(K.resolve(r)), repr(K.Cons(K.Vec([A('error_mode'), A('on')]), K.NIL)))
        click(10, 4)
        r = K.Var()
        self.assertTrue(self.send(m, menu, 'read', r))
        self.assertEqual(K.resolve(r), A('abort'))
        self.assertTrue(self.send(m, menu, 'kill'))
        self.assertEqual(fr.rows, before)
        with self.assertRaises(K.Refusal) as e:
            self.send(m, menu, 'set_item_value', A('colour'), A('on'))
        self.assertIn('choice_refused', str(e.exception.detail))

    def test_win_m8_markers(self):
        # M8, markers (window.md §2.6; standard_io_window.esp "MARKERS",
        # marker.esp): selectors PRINTED-INTERFACE TM-125 p17, bodies OURS.
        # create_marker/2 gives an undrawn 16 x 16 box at (0, 0), listed by
        # get_marker_list/2; draw_marker/2 draws its outline (60 dots,
        # exclusive_or), a second draw_marker/2 changes nothing;
        # move_marker/4 to (100, 50): the old place is clean, the outline
        # is there; set_marker_type/3 `line`: the diagonal, 16 dots;
        # set_marker_size/4 30 x 10: the line from (100, 50) to (129, 59),
        # 30 dots; erase_marker/2: the frame is back as before the marker;
        # a second erase changes nothing; create_marker/7 (the CESP
        # substitute's form) `reverse` 8 x 8 at (200, 100): 64 dots; an
        # unknown type refuses loudly.
        # Injections, OBSERVED (2026-11-26; each from a backup copy,
        # restored by copy, cmp clean; Window, test_fep_bridge.py and
        # test_kl0.py run, all else OK):
        #   G5 draw_marker/2 draws a drawn marker again: this test FAILS,
        #      nothing else.
        #   G6 move_marker/4 does not take the marker off first: this test
        #      FAILS, nothing else.
        #   G7 execute_graphics_command/2 does not know the five-element
        #      draw_string (g_window's): test_win_m8_forms ERRORS, nothing
        #      else.
        #   G8 draw_line_in/7 checks a slanted line after uncover/3 (the
        #      code before the fix): test_win_m8_forms FAILS, nothing else.
        #   G9 draw_line/6 takes every argument as the op:
        #      test_win_m8_forms ERRORS, nothing else.
        #   P10 wake/1's free/2 ignores a permission changed to out or
        #      show: test_win_m7_permission_change FAILS, nothing else.
        #   P11 remove_window/2 keeps a killed window's waiters:
        #      test_win_m7_permission_change FAILS, nothing else.
        #   P12 create/3 ignores the permission(P) option:
        #      test_win_m7_permission_change FAILS, nothing else.
        #   P13 the coordinator's own process held back like a writer
        #      (manager/1 bypass removed): first run (merge 20efface)
        #      NOTHING failed, no run on the route making the coordinator
        #      write into a covered window whose permission is not out.
        #      Since test_win_m7_coordinator_writes (a has_been_selected/1
        #      demon writing into a covered `wait` window from the
        #      coordinator's process): that test ERRORS (would suspend),
        #      nothing else.
        import windev
        import winfb
        X0, Y0 = self.GRAPHICS_AT
        m, w = self.graphics_window()
        fr = windev.device(m).frame
        before = list(fr.rows)
        mk = K.Var()
        self.assertTrue(self.send(m, w, 'create_marker', mk))
        mk = K.resolve(mk)
        self.assertEqual(fr.rows, before)
        ms = K.Var()
        self.assertTrue(self.send(m, w, 'get_marker_list', ms))
        self.assertEqual(self._walk(K.resolve(ms)), [mk])

        def drawn(sel, *args):
            n0 = fr.count()
            self.assertTrue(self.send(m, w, sel, mk, *args), sel)
            return fr.count() - n0
        self.assertEqual(drawn('draw_marker'), 60)
        self.assertEqual(drawn('draw_marker'), 0)
        want = winfb.Frame()
        want.rows = list(before)
        want.command(winfb.FILL << 4 | 2, [X0, Y0, 16, 16, 0, 0])
        want.command(winfb.FILL << 4 | 2, [X0 + 1, Y0 + 1, 14, 14, 0, 0])
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual(drawn('move_marker', 100, 50), 0)
        want.rows = list(before)
        want.command(winfb.FILL << 4 | 2, [X0 + 100, Y0 + 50, 16, 16, 0, 0])
        want.command(winfb.FILL << 4 | 2, [X0 + 101, Y0 + 51, 14, 14, 0, 0])
        self.assertEqual(fr.rows, want.rows)
        self.assertEqual(drawn('set_marker_type', K.Atom('line')), 16 - 60)
        self.assertEqual(drawn('set_marker_size', 30, 10), 30 - 16)
        self.assertEqual([m.get_slot(mk, k) for k in ('x', 'y', 'w', 'h')], [100, 50, 30, 10])
        self.assertEqual(drawn('erase_marker'), -30)
        self.assertEqual(drawn('erase_marker'), 0)
        self.assertEqual(fr.rows, before)
        m2 = K.Var()
        self.assertTrue(self.send(m, w, 'create_marker', 200, 100, 8, 8, K.Atom('reverse'), m2))
        mk = K.resolve(m2)
        self.assertEqual(drawn('draw_marker'), 64)
        ms = K.Var()
        self.assertTrue(self.send(m, w, 'get_marker_list', ms))
        self.assertEqual(len(self._walk(K.resolve(ms))), 2)
        with self.assertRaises(K.Refusal) as e:
            self.send(m, w, 'create_marker', 0, 0, 8, 8, K.Atom('circle'), K.Var())
        self.assertIn('graphics_refused', str(e.exception.detail))

    # -- window M10 (2026-11-26): Pmacs proper ------------------------------
    # The held programs run whole on the stand-ins, each started as a user
    # would start a program: an item added to the system menu (OURS, as
    # the M6/M7 runs add events), chosen after the Login PIMOS run.  The
    # harness classes are OURS: an as_program heir whose goal/1 calls the
    # held entry, and for cal_pmacs the four methods its run/4 asks of the
    # cal program object (cal's own, not loaded).  exshow's class slot
    # `font` is read from `font:kanji_28.font`, which is not held: the run
    # gives that name a directory entry for the held test_11 font (OURS
    # substitute, made in the run only; without it the class is refused,
    # test_win_m10_exshow).
    M10_HARNESS = {
        'exshow': ('exshow', """class m10_exshow has
nature as_program;
instance
:goal(P) :- :go(#exec_show_tmp, "boot", "me:boot.init");
end."""),
        'cal': ('cal_pmacs', """class m10_cal has
nature as_program;
attribute saved := 0;
:keep(Class, B) :- Class!saved := B;
instance
% cal's program object's slot that run/4 sets to the Pmacs window and back
attribute cur_window := 0;
:goal(P) :- :run(#cal_pmacs, "me:boot.init", "me:user.cal", P);
:get_file_menu(P, P);
:get_pmacs_window(P, W) :-
    :create(#cal_pmacs_window, [title("cal"), size(500, 250), position(100, 100)], W);
:load_file_to_buffer(P, File, B) :-
    :create(#editor_text_buffer, B, "cal", 0),
    :retrieve(#directory, F, File, _),
    :load_file(B, F);
:save_buffer(P, File, B) :- :keep(#m10_cal, B);
end."""),
        # papyrus's my_buffer_selecter (my_select.esp.1) with its two other
        # natures, papyrus classes not loaded, as empty classes (OURS)
        'select': ('my_select', """class my_proof_editor has
end.
class my_mode_changer has
end.
class m10_select has
nature as_program;
instance
:goal(P) :-
    :create(#pmacs_window, [editor(#my_buffer_selecter), title("papyrus"),
                            size(500, 250), position(100, 100)], W),
    :create(#editor_text_buffer, B1, "one", 0),
    :create(#editor_text_buffer, B2, "two", 0),
    :set_input_buffer(W, B1),
    :activate(W),
    :get_interpreter(W, I),
    :command_interpret(I);
end."""),
    }
    M10_CLICK = (200, 150)          # inside every M10 program's window
    C_X, C_S, C_Z = 24, 19, 26

    @staticmethod
    def m10_key(c):
        return K.Vec([K.Atom('key'), c])

    @classmethod
    def m10_keys(cls, text):
        return [cls.m10_key(c) for c in K.Str(text).codes()]

    @staticmethod
    def m10_entry(m, d, name):
        got = [K.deref(e.args[1]) for e in Window._walk(m.get_slot(d, 'entries'))
               if K.deref(e.args[0]).text == name]
        return got[0] if got else None

    @staticmethod
    def m10_node(m, path):
        d = m.get_slot(K.ClassRef('simpos##directory'), 'root')
        for name in path.strip('>').split('>'):
            d = Window.m10_entry(m, d, name)
        return d

    def m10_start(self, m, prog, font):
        # the substitute font entry, the added menu item, and the events
        # that choose it
        import fep_bridge as FB
        if font:
            fd = self.m10_node(m, '>sys>font')
            t11 = self.m10_entry(m, fd, 'test_11.font')
            m.set_slot(fd, 'entries', K.Cons(K.Vec([K.Str('kanji_28.font'), t11]),
                                             m.get_slot(fd, 'entries')))
        C = K.ClassRef('simpos##coordinator')
        item = K.Vec([FB.jstr('M10'), K.Atom('m10_' + prog)])
        m.set_slot(C, 'menu', K.Cons(K.Cons(item, K.NIL), m.get_slot(C, 'menu')))
        return [K.Atom('invoke_system_menu'), K.Vec([K.Atom('select'), FB.jstr('M10')])]

    def pmacs_run(self, prog, *batches, font=True):
        # later_run with the held source and the harness compiled in, the
        # program started at the first quiet moment after the login, then
        # each of BATCHES at the next one, the first after a left click in
        # the window (it selects it).  -> (machine, frame, the refusal
        # that ended the run)
        import fep_bridge as FB
        import held
        import windev
        member, harness = self.M10_HARNESS[prog]
        psi = FB.PsiSide()
        m = psi.m
        for src in (held.member_text(member), harness):
            ts, failed = espc.compile_text(src, 'simpos')
            self.assertEqual(failed, {})
            for t in ts:
                m.lib.add(t)
        psi.user = [FB.mouse('rr', *FB.MENU_AT), FB.mouse('l', *FB.LOGIN_ITEM_AT)]
        rest = [lambda mm: self.m10_start(mm, prog, font)] + [list(b) for b in batches]
        if len(rest) > 1:
            rest[1] = [FB.mouse('l', *self.M10_CLICK)] + rest[1]

        def exchange(out):
            if rest and not psi.shell:
                b = rest.pop(0)
                psi.shell, psi.getl = list(b(m) if callable(b) else b), True
            return []
        stop = psi.run(exchange)
        self.assertEqual((rest, psi.shell), ([], []))
        return m, windev.device(m).frame, stop

    def m10_window(self, m):
        # the run's Pmacs window (the coordinator's pmacs_window or heir)
        ws = [w for w in self._walk(m.get_slot(K.ClassRef('simpos##coordinator'), 'windows'))
              if 'pmacs' in w.cid]
        return ws[0] if ws else None

    def m10_rows(self, m, fr):
        # the window's text rows read back from the frame, reverse video
        # read as plain text: -> (rows, the set of reversed (row, column))
        import windev
        w = self.m10_window(m)
        P = m.get_slot(w, 'pane')
        left, top, cols, rows = (m.get_slot(P, k) for k in ('left', 'top', 'cols', 'rows'))
        out, rev = [], set()
        for r, line in enumerate(windev.read_cells(fr, left, top, cols, rows)):
            s, c, i = '', 0, 0
            while i < len(line):
                if line[i] == '[' and i + 2 < len(line) and line[i + 2] == ']':
                    s, i = s + line[i + 1], i + 3
                    rev.add((r, c))
                elif line[i] == '#':
                    s, i = s + ' ', i + 1
                    rev.add((r, c))
                else:
                    s, i = s + line[i], i + 1
                c += 1
            out.append(s.rstrip())
        return out, rev

    def m10_buffer_text(self, m, w=None):
        w = w or self.m10_window(m)
        I = m.get_slot(w, 'interpreter')
        return self.m10_text(m, m.get_slot(I, 'buffer'))

    def m10_text(self, m, B):
        import simpos_fs
        v = K.Var()
        self.assertTrue(self.send(m, B, 'contents', v))
        return simpos_fs.text_of(K.resolve(v).codes())

    def m10_versions(self, m):
        # boot.init's versions in >sys>user>pmpsi: {version: (full name, text)}
        import simpos_fs
        d = self.m10_node(m, '>sys>user>pmpsi')
        out = {}
        for e in self._walk(m.get_slot(d, 'entries')):
            if K.deref(e.args[0]).text == 'boot.init':
                f = K.deref(e.args[1])
                out[m.get_slot(f, 'version')] = (m.get_slot(f, 'full_name').text,
                                                 simpos_fs.text_of(m.get_slot(f, 'contents').codes()))
        return out

    # the mode line of exshow's window (pmacs_display.esp, OURS layout from
    # the screenshots): 99 x 46 text cells, buffer 1 "boot", the file
    M10_MODE = 'PMACS(fundamental)(99,46) *-1* boot >sys>user>pmpsi>boot.init.%d --Top--'
    M10_PINS = {
        'pmacs': ('38ff75a3312808cd9c28ca38de9d94ca5a20ecc8f36aa9a0fd7bd2993f91b204', 131806),
        'editor_menu': ('a1ec90b6d649a416b562ca341112d4ef7c5d24b25b55e181d2669e050acc6374', 136585),
    }

    @classmethod
    def m10_shots(cls):
        # the event batches of the two pinned M10 screens (psi/winshot.py
        # `pmacs` and `editor_menu`): exshow's window after `Hi`, C-n, `x`,
        # C-x C-s; the EDITOR MENU opened after `Hi`
        import fep_bridge as FB
        k = cls.m10_key
        return dict(pmacs=(cls.m10_keys('Hi') + [k(14)] + cls.m10_keys('x') + [k(cls.C_X), k(cls.C_S)],),
                    editor_menu=(cls.m10_keys('Hi'), [FB.mouse('r', 300, 200)]))

    def test_win_m10_exshow(self):
        # M10: the HELD disc/exshow.esp (IFS source) runs whole on the
        # Pmacs stand-ins.  Its exec_show_tmp go/3 makes a pmacs_window
        # ([title("boot"), size(1100,700), position(0,0)]), creates the
        # buffer "boot" in the pool (create/4), read_file/4s me:boot.init
        # into it, set_input_buffer/2, activate/1, set_font/2 (its class
        # slot's font), flash/1, then command_interpret/1:
        #   - the screen: the file's lines, the mode line reversed over the
        #     whole row, the echo line `Read! >sys>user>pmpsi>boot.init.1`;
        #   - `Hi`, C-n, `x`, C-x C-s: the text edited at the point (C-n
        #     keeps the column, or the line's end), the new version
        #     boot.init.2 written with it, version 1 kept, the echo line
        #     `Written! ...boot.init.2`, the mode line naming version 2;
        #     the frame pinned (psi/winshot.py `pmacs`);
        #   - `Hi`, then C-x C-z: the loop ends and exshow kill/1s the
        #     window: off the coordinator's list, the program ended,
        #     nothing written;
        #   - without the substitute font entry the class is refused at its
        #     slot's initial value (when set_font/2 first reads it).
        # Injections, OBSERVED: the table after test_win_m10_keys.
        import windev
        X, S, Z = self.C_X, self.C_S, self.C_Z
        k = self.m10_key
        m, fr, stop = self.pmacs_run('exshow')
        self.assertEqual(stop.cause, 'would suspend')
        w = self.m10_window(m)
        self.assertEqual((w.cid, m.get_slot(w, 'title').text), ('simpos##pmacs_window', 'boot'))
        v = self.m10_versions(m)
        self.assertEqual(sorted(v), [1])
        name1, t1 = v[1]
        self.assertEqual(name1, '>sys>user>pmpsi>boot.init.1')
        lines = t1.split('\n')
        self.assertEqual(lines[1], '[')
        rows, rev = self.m10_rows(m, fr)
        self.assertEqual(len(rows), 48)
        self.assertEqual(rows[:len(lines)], [ln[:99] for ln in lines])
        self.assertEqual(rows[46], self.M10_MODE % 1)
        self.assertEqual({c for r, c in rev if r == 46}, set(range(99)))
        self.assertEqual(rows[47], 'Read! >sys>user>pmpsi>boot.init.1')
        m, fr, stop = self.pmacs_run('exshow', *self.m10_shots()['pmacs'])
        want = ['Hi' + lines[0], '[x'] + lines[2:]
        self.assertEqual(self.m10_versions(m), {1: (name1, t1),
                                                2: ('>sys>user>pmpsi>boot.init.2', '\n'.join(want))})
        self.assertEqual(self.m10_buffer_text(m), '\n'.join(want))
        rows, rev = self.m10_rows(m, fr)
        self.assertEqual(rows[:len(want)], want)
        self.assertIn((1, 2), rev)          # the cursor, after the x
        self.assertEqual(rows[46], self.M10_MODE % 2)
        self.assertEqual(rows[47], 'Written! >sys>user>pmpsi>boot.init.2')
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.M10_PINS['pmacs'])
        m, fr, stop = self.pmacs_run('exshow', self.m10_keys('Hi'), [k(X), k(Z)])
        self.assertIsNone(self.m10_window(m))
        self.assertIn('has ended', stop.detail)
        self.assertEqual(sorted(self.m10_versions(m)), [1])
        m, fr, stop = self.pmacs_run('exshow', font=False)
        self.assertEqual((stop.cause, stop.detail), ('class not generated', 'simpos##exec_show_tmp class '
                                                     'slot font: its initialisation fails'))

    def test_win_m10_keys(self):
        # M10, the default bindings (standard_editor.esp, OURS, gap G6) on
        # exshow's buffer: `ab`, C-b, C-d, C-e, DEL, `Z`, C-n, C-a, C-k,
        # C-k, `Q`, C-p, `R`, C-f, `S` give the text an Emacs gives (line
        # 1, `[`, killed with its newline; C-n and C-p keep the column or
        # take the line's end), shown on the screen; the mode line still
        # names version 1 (nothing saved).  Then the help key (bound to
        # nothing) echoes `Undefined key`, the text unchanged, and so does
        # C-x q (q bound in no prefix table).
        # Injections, OBSERVED: see the table below this test.
        k = self.m10_key
        ks = self.m10_keys
        seq = (ks('ab') + [k(2), k(4), k(5), k(127)] + ks('Z') + [k(14), k(1), k(11), k(11)] + ks('Q')
               + [k(16)] + ks('R') + [k(6)] + ks('S'))
        m, fr, stop = self.pmacs_run('exshow', seq)
        lines = self.m10_versions(m)[1][1].split('\n')
        self.assertEqual(lines[1], '[')
        want = ['aR' + lines[0][0] + 'S' + lines[0][1:-1] + 'Z', 'Q' + lines[2]] + lines[3:]
        self.assertEqual(self.m10_buffer_text(m), '\n'.join(want))
        rows, _rev = self.m10_rows(m, fr)
        self.assertEqual(rows[:len(want)], [ln[:99] for ln in want])
        self.assertEqual(rows[46], self.M10_MODE % 1)
        self.assertEqual(rows[47], 'Read! >sys>user>pmpsi>boot.init.1')
        m, fr, stop = self.pmacs_run('exshow', seq + [k(0x8006)])
        self.assertEqual(self.m10_rows(m, fr)[0][47], 'Undefined key')
        self.assertEqual(self.m10_buffer_text(m), '\n'.join(want))
        m, fr, stop = self.pmacs_run('exshow', [k(self.C_X)] + ks('q'))
        self.assertEqual(self.m10_rows(m, fr)[0][47], 'Undefined key')

    def test_win_m10_scroll(self):
        # M10, the display's scrolling and the mode line's place field
        # (pmacs_display.esp scrolled/2, drop_lines/3, place/3, all OURS):
        # 50 RETURNs at the start of exshow's buffer (62 lines, 46 text
        # rows) put the point on line 50, so the first shown line is 5
        # (the point's line the last row) and the place `--8%--`
        # (5 * 100 / 62); C-n x 6: line 11, `--17%--` (two digits); C-n x 20
        # (the last line): `--Bot--`; then C-p x 60: line 1 above the
        # screen, the first shown line 1, `--1%--`; C-p: `--Top--`.  The
        # screen's rows are the buffer's lines from the first shown one.
        # Implemented, NOT exercised by any test: status_window(off) (no
        # mode line), a point past the last column (no cursor).
        # Injections, OBSERVED: the table after test_win_m10_keys (Q1, Q2).
        k = self.m10_key
        R = [k(13)] * 50
        mode = self.M10_MODE.replace(' --Top--', ' --%s--') % (1, '%s')
        for seq, top, place in ((R, 5, '8%'), (R + [k(14)] * 6, 11, '17%'),
                                (R + [k(14)] * 20, 16, 'Bot'),
                                (R + [k(14)] * 20 + [k(16)] * 60, 1, '1%'),
                                (R + [k(14)] * 20 + [k(16)] * 61, 0, 'Top')):
            m, fr, stop = self.pmacs_run('exshow', seq)
            lines = self.m10_buffer_text(m).split('\n')
            self.assertEqual(len(lines), 62)
            D = m.get_slot(self.m10_window(m), 'display')
            self.assertEqual(K.deref(m.get_slot(D, 'top')), top)
            rows, _rev = self.m10_rows(m, fr)
            shown = [ln[:99].rstrip() for ln in lines[top:top + 46]]
            self.assertEqual(rows[:46], shown + [''] * (46 - len(shown)))
            self.assertEqual(rows[46], mode % place)

    # Window M10 injections, OBSERVED (2026-11-26; each in a private copy
    # of psi/, the worktree untouched; test_espc.py, test_fep_bridge.py and
    # test_kl0.py run; all else OK):
    #   K1 C-d bound to backward_character: first run NOTHING failed (the
    #      keys test's sequence then killed the line, hiding the deleted
    #      character); the sequence was changed (C-d before C-e), then M10
    #      keys FAIL/ERROR, nothing else.
    #   S1 a save overwrites the latest version (kl0 new_version keeps the number; the plan's injection): M10 exshow, M10 menu (ERROR) FAIL/ERROR, nothing else.
    #   D1 the mode line drawn plain, not reversed: M10 exshow, M10 menu (its pinned frame) FAIL/ERROR, nothing else.
    #   D2 a text row once drawn is never drawn again: M10 exshow, keys, menu, cal FAIL/ERROR, nothing else.
    #   M1 an EDITOR MENU item's value not given to the window: M10 menu; test_fep_census (menu_chosen/2 row success) FAIL/ERROR, nothing else.
    #   R1 the right button not routed to the window: M10 menu (ERROR) FAIL/ERROR, nothing else.
    #   V1 set_input_buffer/2 does not tell the interpreter: M10 exshow, menu; keys, cal, select (ERROR); test_fep_census FAIL/ERROR, nothing else.
    #   C1 the editor class from the option only (a subclass's slot ignored): M10 cal FAIL/ERROR, nothing else.
    #   P1 select_buffer/2's primary does nothing: M10 select; test_fep_census FAIL/ERROR, nothing else.
    #   X1 the window's datum as the term {data, X} again (the bug found): M4 console, M6 selection, M7 console move; test_fep_bridge.py Console FAIL/ERROR, nothing else.
    #   Q1 scrolled/2 never moves the first shown line: M10 scroll FAIL, nothing else.
    #   Q2 place/3's --Bot-- clause removed: M10 scroll FAIL, nothing else.

    # the EDITOR MENU's items (standard_editor.esp show_menu/1: verbatim
    # from IPSJ 36239 p5), opened by the right button at (300, 200)
    M10_MENU = ['ABORT', 'List Buffers', 'Save All Files', 'Set Font', 'Set Echo Font',
                'Set Window Size', 'From Whiteboard', 'To Whiteboard']

    @staticmethod
    def m10_item(i):
        # a left click on item I of the EDITOR MENU opened at (300, 200)
        # (its items from y 221, 16 dots each: menu_pane.esp's layout)
        import fep_bridge as FB
        return FB.mouse('l', 320, 221 + 16 * i + 8)

    def test_win_m10_menu(self):
        # M10, the EDITOR MENU (IPSJ 36239 p5, SCREENSHOT; window.md §2.11):
        # with exshow's window up and `Hi` typed, the right button on it
        # (the coordinator gives the window right_click/3; its input gets
        # mouse#r, bound to show_menu by standard_editor's table) opens a
        # pop-up titled EDITOR MENU at the mouse with the eight items, one
        # column (OURS); the frame pinned (psi/winshot.py `editor_menu`).
        #   - List Buffers: the menu closes, the echo line `Buffers: boot`;
        #   - Save All Files: the modified buffer written, version 2, echo
        #     `Written! ...boot.init.2`;
        #   - ABORT: the menu closes, nothing else (the frame as before the
        #     right button);
        #   - Set Font: refused loudly, set_font_by_menu/1 not stood in;
        #   - a left click away from the menu closes it, no item chosen.
        # Injections, OBSERVED: the table after test_win_m10_keys.
        import fep_bridge as FB
        import windev
        C = K.ClassRef('simpos##coordinator')
        hi = self.m10_keys('Hi')
        right = [FB.mouse('r', 300, 200)]
        m, before, _ = self.pmacs_run('exshow', hi)
        before = list(before.rows)
        m, fr, stop = self.pmacs_run('exshow', *self.m10_shots()['editor_menu'])
        self.assertEqual(stop.cause, 'would suspend')
        M = m.get_slot(C, 'menu_pane')
        x, y, wd, it = (K.resolve(m.get_slot(M, k)) for k in ('x', 'y', 'w', 'items_top'))
        self.assertEqual((x, y, it), (300, 200, 221))
        self.assertEqual(windev.read_cells(fr, x + 2, y + 3, wd // 11, 1), ['   EDITOR MENU'])
        for i, label in enumerate(self.M10_MENU):
            # each label centred (menu_pane.esp), so read at every offset
            self.assertTrue(any(label in windev.read_cells(fr, x + 2 + d, it + 16 * i + 1, (wd - 4) // 11, 1)[0]
                                for d in range(11)), label)
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), self.M10_PINS['editor_menu'])
        m, fr, stop = self.pmacs_run('exshow', hi, right, [self.m10_item(1)])
        self.assertEqual(K.deref(m.get_slot(C, 'menu_pane')), 0)
        self.assertEqual(self.m10_rows(m, fr)[0][47], 'Buffers: boot')
        m, fr, stop = self.pmacs_run('exshow', hi, right, [self.m10_item(2)])
        self.assertEqual(self.m10_rows(m, fr)[0][47], 'Written! >sys>user>pmpsi>boot.init.2')
        self.assertEqual(self.m10_versions(m)[2][1].split('\n')[0][:4], 'Hi% ')
        m, fr, stop = self.pmacs_run('exshow', hi, right, [self.m10_item(0)])
        self.assertEqual(K.deref(m.get_slot(C, 'menu_pane')), 0)
        self.assertEqual(fr.rows, before)
        m, fr, stop = self.pmacs_run('exshow', hi, right, [FB.mouse('l', 800, 100)])
        self.assertEqual(K.deref(m.get_slot(C, 'menu_pane')), 0)
        self.assertEqual(fr.rows, before)
        m, fr, stop = self.pmacs_run('exshow', hi, right, [self.m10_item(3)])
        self.assertIn('standard_editor:set_font_by_menu/1 (not in the stand-in)', stop.detail)

    def test_win_m10_cal(self):
        # M10, cal's Pmacs (HELD cal2.12/cal_pmacs.esp, IFS source): its
        # cal_pmacs_window (a pmacs_window whose `editor` slot is
        # #cal_pmacs_editor) gets a cal_pmacs_editor, so the held editor
        # class's own binding `:command(Editor,pf#11,cal_menu)` comes
        # before the stand-in defaults.  The held cal_pmacs run/4 runs
        # whole (its cal program object OURS, M10_HARNESS):
        # load_file_to_buffer, get_pmacs_window (title, size(500,250),
        # position(100,100): 44 x 14 text cells), set_input_buffer/2,
        # goto_beginning/1, set_input_position/1, activate/1,
        # command_interpret/1:
        #   - `ab` typed: the buffer's text, the default keys still bound;
        #   - pf#11: the held cal_menu/1 runs, and is refused at the class
        #     it creates, cal_op_menu (cal's, not loaded);
        #   - C-x C-z: the loop ends, run/4 deactivate/1s the window (off
        #     the screen), takes current_buffer/2 and save_buffer/3s it: the
        #     buffer kept by the harness has the edited text; the program
        #     ends.
        # Injections, OBSERVED: the table after test_win_m10_keys.
        k = self.m10_key
        m, fr, stop = self.pmacs_run('cal', self.m10_keys('ab'))
        w = self.m10_window(m)
        self.assertEqual((w.cid, K.deref(m.get_slot(w, 'editor')).cid),
                         ('simpos##cal_pmacs_window', 'simpos##cal_pmacs_editor'))
        self.assertEqual([m.get_slot(w, s) for s in ('x', 'y', 'columns', 'rows')], [100, 100, 44, 16])
        t1 = self.m10_versions(m)[1][1]
        self.assertEqual(self.m10_buffer_text(m), 'ab' + t1)
        rows, _rev = self.m10_rows(m, fr)
        self.assertEqual(rows[0], ('ab' + t1)[:44])
        self.assertEqual(rows[14][:36], 'PMACS(fundamental)(44,14) *-1* cal >')
        m, fr, stop = self.pmacs_run('cal', self.m10_keys('ab') + [k(0x8100 + 11)])
        self.assertEqual(stop.detail, 'send simpos##cal_op_menu:create/2 (class class not loaded)')
        m, fr, stop = self.pmacs_run('cal', self.m10_keys('ab') + [k(self.C_X), k(self.C_Z)])
        self.assertIsNone(self.m10_window(m))
        self.assertIn('has ended', stop.detail)
        B = K.deref(m.get_slot(K.ClassRef('simpos##m10_cal'), 'saved'))
        self.assertEqual(self.m10_text(m, B), 'ab' + t1)

    def test_win_m10_select(self):
        # M10, papyrus's my_buffer_selecter (HELD demo/EDITOR/
        # my_select.esp.1, IFS source): a pmacs_standard_editor heir with
        # after-demons on select_buffer/1, select_buffer/2 and
        # list_buffers/1 (no primaries: SIMPOS's are combined with them,
        # window.md §2.12).  A pmacs_window made with
        # editor(#my_buffer_selecter), visiting buffer "one" of the pool
        # [two, one]: C-x b (select_buffer/1, the stand-in's next pooled
        # buffer) runs the stand-in primaries, the window now visits
        # "two", then the held after-demon of select_buffer/2, which is
        # refused at its first send, show_mode_menu/2 (papyrus's
        # my_mode_changer, not loaded: an empty class here).
        # Injections, OBSERVED: the table after test_win_m10_keys (P1).
        k = self.m10_key
        m, fr, stop = self.pmacs_run('select', [k(self.C_X)] + self.m10_keys('b'))
        w = self.m10_window(m)
        E = K.deref(m.get_slot(w, 'editor'))
        self.assertEqual(E.cid, 'simpos##my_buffer_selecter')
        I = m.get_slot(w, 'interpreter')
        self.assertEqual(m.get_slot(m.get_slot(I, 'buffer'), 'name').text, 'two')
        self.assertIn('my_buffer_selecter:show_mode_menu/2', stop.detail)

    def test_win_m10_dedit_compiles(self):
        # M10: cal's dedit.esp (HELD cal-esp deb2.12, the editor whose
        # control_c/control_x tables window.md §5.2 cites) compiles with the
        # key macros, one class, and its only refused predicate is exit/1
        # (an if-then-else, not modelled); it is not run (its editor class
        # needs cal's other classes).
        import held
        ts, failed = espc.compile_text(held.member_text('dedit'), 'simpos')
        self.assertEqual(failed, {})
        self.assertEqual([t.refusals for t in ts],
                         [[(('exit', 1, 0x35), 'if-then-else ->', 'not modelled')]])

if __name__ == '__main__':
    unittest.main()
