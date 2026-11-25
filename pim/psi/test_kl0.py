#!/usr/bin/env python3
"""Tests of the KL0 interpreter (psi/kl0.py) on the held compiled code.  OURS.

    python3 -I psi/test_kl0.py        (a few seconds; reads the .ptf files and
                                       pimos.tar.Z from the repo's archives in
                                       memory, extracts nothing)

1. The opcode table (psi/kl0_opcodes.tsv) is the dispatch: one handler per
   witnessed row, no handler without a row, every row with a witness.
   The four string rows (blt 0b, 1c, 23, 2b) run on their witness
   operands, new_string with S != T included (view_select_menu change/3).
   Step 3e's census semantics (Step3eCensus): slot constants and the
   uncaught raise.  Step 3e's rows (Step3eRows) run on held kappa code beside its held
   source where one runs (get_integer, $or$9, make_nest_vector), else on
   the handler.
2. pimfep##fep_command_code_table:convert/3, both ways, against the
   `fep#name => code` macros of PIMOS's pimos.vmac (measured 2026-11-24):
   96 names agree, 4 only in the FEP table, 8 only in PIMOS; code -> name
   misses 5 names whose code an earlier clause answers and cuts;
   convert(_,_) has no solution.
3. Paragraph classes against their held ESP source (p_icon.esp,
   p_itool.esp, p_buf.esp, version.esp): the results the source predicts.
   paragraph_version gives "3500" where the held source says "3200": the
   binary and the held source are different builds (pinned as a known
   skew, not a fault).
   scroll_bottom_icon's code/4 has two primaries, run as alternatives,
   and time_graph_window:go/1 refuses at its first SIMPOS send.  (The
   104 classes have no before- or after-demons: 14 methods have more
   than one primary, none has a demon.)
4. Slot initialisation (TM-388 §3.5 pp.49-50), on kappa alone against its
   held source: new/2 runs the slot-initialisation predicates (all 424
   held ones have arity 1, pinned), nested creation (an initialiser that
   creates a class with its own initialiser), two-goal initialisers, and
   `slot is Class` as a new instance (TM-388 p.49 (3)).
5. The census of the 104 classes that need no SIMPOS (103 with methods):
   each method called once with unbound arguments; totals and the refusal
   ranking pinned.

Discriminating (2026-11-24; each bug injected into kl0.py from a backup
copy, the observed failures recorded, the file restored from the backup):
  - unification: two integers always unify: only test_list_index_buffer
    fails (convert/3 indexes its codes through the hash table, not unify);
  - cut: d2 (cut_proceed) returns without cutting: test_cut fails and
    test_list_index_buffer errors (create/1 gives more than one solution);
  - an opcode: blt 41 subtract computes A_B - A_A: only
    test_predicate_num_switch_icon fails;
  - dispatch: the send takes the receiver from A0 instead of A_R:
    test_list_index_buffer and test_predicate_num_switch_icon error,
    test_census and test_simpos_refusal fail;
  - dispatch: the primaries tried in reverse order: test_two_primaries
    and test_census fail;
  - the register barrier: pmi dd/de cut to the current stack height
    instead of the barrier in A_A: only test_census fails (success 304,
    failure 10: pimmcsp##pseudo_csp_csbreak_address_table csp_mm_reg/3,
    whose source is not held, succeeds instead of failing).
Slot initialisation (2026-11-24, injected into kl0.py from a backup in the
session scratchpad, restored with cp and checked with cmp; both test files
run; observed):
  - a failing initialiser ignored (new/2 succeeds, the slot 0): only
    test_espc test_failure_fails_new fails;
  - the initialiser's value taken from A1, not A0: errors in
    test_hash_table, test_nested_new, test_two_goals, and in test_espc
    test_class_slot, test_instance_slots_and_after_demon,
    test_printed_process_slots, test_self, test_stream_runs; failures in
    test_fep_census and test_on_after_gets_further;
  - class slots initialised by code left 0: only test_espc test_class_slot;
  - one initial value per slot, shared by every instance: only
    test_nested_new;
  - `slot is Class` stores the class object: only test_slot_is_class
    (an error).
  (Rerun with the session's injection script after any change to the
  tests; the set above was observed on the final tests.)
String built-ins and :refute (2026-11-24, injected the same way into
kl0.py, and into espc.py for the last; both test files run; observed):
  - new_string puts the string in the T register: only
    test_string_cells (an error);
  - string_element reads element I+1: test_string_cells and test_espc
    test_string fail;
  - set_string_element does not store: test_string_cells and test_string
    fail;
  - string/3 gives the type as the length: test_string_cells fails,
    test_string errors;
  - :refute leaves the receiver in A0: only test_espc test_refute (an
    error);
  - espc's head-save fix reverted: test_espc test_string errors and
    test_counts fails;
  - espc emits new_string with L and S swapped: only test_espc
    test_string (an error);
  - espc gives string/3's two outputs one register: the compiler raises
    (not a refusal) on paragraph and kappa2, so every test_espc test
    that compiles them errors: two setUpClass,
    test_no_internal_refusal, test_only_witnessed_opcodes, test_kappa2,
    test_aspect_differences, test_counts, test_named_exact.
  - integer/1 (step 3c) refuses an unbound argument instead of failing:
    test_step3c_cells errors here; test_espc test_on_after_gets_further
    errors and test_fep_census fails.
  - search_character/5 (step 3c) starts one past B: nothing here;
    test_espc test_held_source fails.
Step 3d rows (2026-11-24, injected into kl0.py from a backup in the
session scratchpad, restored with cp and checked with cmp; both test
files run; observed):
  - vector_to_list (blt 6e) writes the list over A_V instead of A_L: only
    test_step3d_cells fails;
  - put_vector_4 (pmi b4) makes three elements: only test_step3d_cells
    fails (the compiled and held paragraph code fail alike, so test_espc's
    behaviour census does not see it);
  - put_variable_t (pmi a1) with A != X binds only A_A: only
    test_step3d_cells fails; the FEP census totals are unchanged.
Step 3e's pmi ca, if_not_constant (2026-11-24, injected into kl0.py with
the session's inject.py: backup, patch, both test files run, restored with
cp and checked with cmp; observed):
  - always jump (equal falls through no more): test_if_not_constant and
    test_census fail here; test_espc test_census (behaviour) and
    test_fep_census fail;
  - never jump: only test_if_not_constant here (set_all/5 has no try chain,
    so set_all_at fails); test_espc test_fep_census fails;
  - an unbound A0 jumps: test_if_not_constant and test_census here;
    test_espc test_fep_census;
  - the jump base cell + 2 instead of + 3: only test_if_not_constant.
Step 3e's blt f2, if_identical_f2 (2026-11-24, same method; observed):
  - inverted (jump when identical): only test_if_identical_f2 here;
    test_espc test_fep_census fails;
  - the jump base cell + 3 instead of + 2: test_if_identical_f2 here;
    test_espc test_fep_census.
Step 3e's rows 9a/9b, b1/b5/b6/b7, 50/51/54/55 and R != A for 40/49
(2026-11-24, same method, both test files run; observed):
  - 9a/9b skip a cell: test_interrupt_brackets here; test_espc
    test_fep_census errors;
  - b1 makes two elements, b6 five, b7 n - 1: test_vector_puts only (each);
  - (step 3f, 2026-11-25) b7 with A != 0 refused again: test_vector_puts
    errors; a non-zero second byte accepted: test_vector_puts fails;
    test_espc passes both times (the one moved census row is refused
    either way);
  - and as or, or as xor, shift_left by n - 1, shift_right by n - 1:
    test_bit_operations only (each);
  - shift_left wraps at 32 bits instead of refusing at 2**31:
    test_bit_operations only (test_kl0 alone run; first seen passing, when
    the test's overflow case refused at string_element instead, so the
    test now checks the refusal is shift_left's);
  - divide_immediate into A_A: test_result_register only; add into A_A:
    test_result_register and test_step3c_cells.
  test_espc passes under every injection but the first: its census pins
  see only the opcodes' presence, not their arithmetic.
  - (step 3g, 2026-11-25) multiply_constant with R != A refused again
    (blt 48, witness p_hwin.esp:233 `48 00 02 03`): test_result_register
    errors and test_census fails here; test_espc
    test_step3f_census_recipes fails (editor get_title/3 back at the
    operand refusal).
Step 3e's census semantics (2026-11-24, same method; observed):
  - slot constants not marked: test_census and test_slot_constant here;
    test_espc test_get_window;
  - marked but the dispatch ignores the mark: test_census and
    test_slot_constant here; test_espc passes (its FEP pin counts
    outcomes, not causes);
  - raise/2 not special (refused as SIMPOS again): test_uncaught_exception
    errors here; test_espc test_fep_census;
  - raise/2 fails instead: test_uncaught_exception here; test_espc
    test_fep_census.
The source check's opcode rows (2026-11-25, injected into kl0.py, restored
by cp from a backup and cmp-checked; observed):
  - blt 19 new_heap_vector refusing V != N again: test_result_register
    errors and test_census fails here; test_espc test_fep_census fails.
  The mnemonic renames (42-45, a4, a5, 24, 2b, blt 45/46/48/49) change
  only names and were not injected: Machine() raises ValueError for a
  table row with no handler of its name (kl0.py load), which the suite
  runs on every machine it builds.
String identity (2026-11-25; each injected into kl0.py or
standin/list_index.esp by the session's variant.py, restored by copy and
cmp-checked; both test files run; observed):
  - unify compares strings by content again: test_unify_and_identical
    only (test_espc passes: equal_key/2 compares contents anyway, and the
    census's arguments are unbound);
  - == (identical) compares strings by content again:
    test_unify_and_identical only;
  - list_index equal_key/2 reduced to unification: test_espc
    test_string_keys only;
  - string/3 refuses a non-string again: test_string_is_a_type_test
    errors and test_census fails here; test_espc test_list_index,
    test_hash_index and test_string_keys error (equal_key/2's type test
    is refused on an atom key) and test_fep_census fails.
Step 3g's switches (Step3gSwitches: pmi c6, ce, c3, c1, ff, tables
cd03/cd04; 2026-11-25; each injected into kl0.py or kl0_opcodes.tsv from
a backup, restored by cp and cmp-checked; both test files run; observed):
  - c6 sends a list to the atom path: test_get_bfs_list_only fails here;
    test_espc passes;
  - c6 sends a vector to the unbound target: test_receiver_send errors
    here; test_espc passes;
  - ce's key length N - 1: test_make_com errors and test_receiver_send
    fails here; test_espc test_fep_census and test_step3f_census_recipes
    fail;
  - ff's target cell + 3: test_get_bfs_list_only errors here; test_espc
    test_fep_census and test_step3f_census_recipes fail;
  - the hash register always A0: test_make_com and test_receiver_send
    error here; test_espc passes;
  - the pmi c3 row dropped: test_make_com and test_receiver_send error,
    test_census and test_handlers_are_the_table fail here; test_espc
    passes;
  - cc reading its constant with const_cell (no vector keys): only
    test_get_tap_type errors; test_espc passes.
Step 3h's rows (Step3hRows: pmi 34 get_vector_4, pmi 35 get_vector_5,
receiver.esp:669 and :680; 2026-11-25; injected into kl0.py or
kl0_opcodes.tsv from a backup, restored by cp and cmp-checked; both test
files run; observed):
  - pmi 34 taking 3 elements: test_get_vector_4 and
    test_nonzero_bytes_refused fail here; test_espc passes;
  - the pmi 35 row and its handler dropped: test_get_vector_5 and
    test_handlers_are_the_table fail, test_nonzero_bytes_refused errors
    here; test_espc test_fep_census and test_step3f_census_recipes fail;
  - the non-zero second/third byte refusal removed: only
    test_nonzero_bytes_refused fails; test_espc passes.
Step 3h's blt e1 (if_integer: p_what.esp:88, g_window.esp:147,
p_MAIN.esp:723; injected the same way; observed):
  - the branch inverted (jump on an integer): test_if_integer and
    test_census fail here; test_espc test_fep_census,
    test_step3f_census_recipes and test_step3h_scsi_mode fail;
  - the non-zero second byte refusal removed: only test_if_integer
    fails; test_espc passes.
Step 3i's rows (Step3iRows: pmi 3b get_val_var_list, pmi 6c
execute_local_switch; LOADER.ESP:118-126 and RDMSOPE.ESP:285-291;
2026-11-25; injected into kl0.py from a backup, restored by cp and
cmp-checked; both test files run; observed):
  - 3b not unifying the car with X_H: test_append and
    test_get_bfs_list_only fail here; test_espc passes;
  - 6c sending a list to its const target: test_append and
    test_get_bfs_list_only fail here; test_espc test_fep_census and
    test_step3f_census_recipes fail;
  - 6c refusing a c6 entry: test_get_bfs_list_only errors here; test_espc
    test_fep_census and test_step3f_census_recipes fail.
Step 3i's blt 00 atom and blt e0 if_atom (test_atom: as_pred.esp:419-422,
g_window.esp:146-149, bar2_h.esp:135; injected the same way; observed):
  - e0's branch inverted (jump on an atom): only test_atom fails; test_espc
    passes;
  - blt 00 succeeding on anything: only test_atom fails; test_espc passes.
Step 3i's pmi c8 switch_on_vector_else (test_switch_on_vector_else:
HLCSESITTK.ESP:408-424, BCMGETREC.ESP:124-160; injected the same way;
observed):
  - c8 sending an unbound argument to its vector path: test_census and
    test_switch_on_vector_else fail here; test_espc test_fep_census and
    test_step3f_census_recipes fail;
  - 6c into a c8 swapping the vector and else targets: only
    test_switch_on_vector_else fails; test_espc passes.
Step 3i's blt 1a new_stack_vector (test_new_stack_vector: mcd.esp:112-116,
KP_BFMOM.ESP:181-185; injected the same way; observed):
  - elements 0 instead of fresh variables: only test_new_stack_vector
    fails; test_espc passes;
  - V and N swapped: test_new_stack_vector errors here; test_espc
    test_fep_census and test_step3f_census_recipes fail.
Step 3i's pmi c9 fix ([] only to the first target; test_switch_on_list_nil:
cts_post.esp:18-21) and the new guards (injected the same way; observed):
  - c9 sending any atomic value to its first target: test_switch_on_list_nil
    fails here; test_espc test_fep_census and test_step3f_census_recipes
    fail;
  - the 6c targets-differ guard removed: only test_other_entries_refused
    errors; test_espc passes;
  - c8's zero-high-half guard removed: only test_switch_on_vector_else
    fails; test_espc passes.
Step 3i's blt 05 heap_vector (test_heap_vector: KPEXTENT.ESP:109-120;
injected the same way; observed):
  - the heap check dropped (any vector answers): only test_heap_vector
    fails; test_espc passes.
"""
import os
import sys
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kl0 as K  # noqa: E402

A = K.Atom
_M = None


def machine():
    global _M
    if _M is None:
        _M = K.Machine(K.load_six())
    return _M


_KM = None


def kappa_machine():
    """A machine with package kappa loaded alone (shared: about 4 s)."""
    global _KM
    if _KM is None:
        lib = K.LB.Librarian()
        lib.load_held(pkgs=['kappa'])
        _KM = K.Machine(lib)
    return _KM


def send(m, recv, name, *args):
    """All solutions of :name(recv, args...): each the resolved ARGS."""
    regs = list(args) + [recv]
    return [[K.resolve(a) for a in args] for _ in m.solve_send(recv, name, regs)]


class Table(unittest.TestCase):
    def test_handlers_are_the_table(self):
        rows = K.load_table()
        keys = [(r['class'], r['opcode']) for r in rows]
        self.assertEqual(len(keys), len(set(keys)), 'an opcode with two rows')
        for r in rows:
            self.assertTrue(r['witness'].strip(), r)
            # step 3k (owner's rule of 2026-11-25): a row may be an
            # INFERENCE, labelled so in its status, its meaning and its
            # witness column; every other row is KNOWN-PLAINTEXT
            self.assertIn(r['status'], ('KNOWN-PLAINTEXT', 'INFERENCE'), r)
            if r['status'] == 'INFERENCE':
                self.assertIn('INFERENCE', r['meaning'], r)
        self.assertEqual([(r['class'], r['opcode']) for r in rows if r['status'] == 'INFERENCE'],
                         [('blt', '94')])
        m = machine()
        self.assertEqual(set(m.handlers), set(keys))
        ops = {n[3:] for n in dir(K.Machine) if n.startswith('op_')}
        self.assertEqual(ops, {r['mnemonic'] for r in rows})
        # 100 before step 3c's nine rows (blt 01 06 10 16 32 33 40 5c 68),
        # 109 before step 3d's four (blt 6e 34, pmi b0 b4), 113 before
        # step 3e's pmi ca and blt f2, 125 before step 3g's seven (pmi c1
        # c3 c6 ce ff, tables cd03 cd04), 132 before step 3h's pmi 34 35 and blt e1,
        # 135 before step 3i's pmi 3b, 6c, c8 and blt 00, e0, 1a, 05,
        # 142 before step 3k's blt 6f and 94
        self.assertEqual(len(rows), 144)

    def test_if_identical_f2(self):
        # blt f2 (step 3e, 2026-11-24): g_window's two disjunctions, run
        # on the held code.  $or$0/3 (g_window.esp:15-17 `( Display ==
        # color,!, create_pairs(Win,ViewMode); true )`): color goes on into
        # create_pairs, which sends to the unbound window; anything else
        # jumps to `true`.  $or$1/3 (g_window.esp:24-27 `( ViewMode ==
        # act,!, :set_view(Win,pe_view) ; :set_gid(Win,Obj!g_id), ...)`):
        # act sends set_view/2, anything else reads the slot g_id
        m = machine()
        cid = 'paragraph##g_window'
        code = m.code(cid)
        ps = {(p.name, p.arity): p for p in m.lib.templates[cid].locals}

        def run(name, d):
            try:
                return sum(1 for _ in m.solve((code, ps[(name, 3)].offset), [K.Var(), K.Var(), A(d)]))
            except K.Refusal as e:
                return e.detail.split(' of ')[0].split(' to ')[0]
        self.assertEqual([run('$or$0', d) for d in ('color', 'act', 'mono')],
                         ['send set_color_pair/3', 1, 1])
        self.assertEqual([run('$or$1', d) for d in ('color', 'act', 'mono')],
                         ['slot g_id', 'send set_view/2', 'slot g_id'])

    def test_if_not_constant(self):
        # pmi ca (step 3e, 2026-11-24): the first-clause guard.  The handler
        # on its operands: unbound and equal fall through (cell + 2), any
        # other bound value jumps (cell + 3 + s16), R != 0 refuses
        m = machine()
        code = types.SimpleNamespace(id='test', cells={1: (1, 0x00, 0, 256)},
                                     t=types.SimpleNamespace(symbols=[]))
        for x, want in ((K.Var(), 2), (256, 2), (255, 3 + 5), (K.Atom('nil'), 3 + 5),
                        (K.Cons(1, K.NIL), 3 + 5)):
            m.reset()
            m.x[0] = x
            m.op_if_not_constant(code, 0, 0, 0, 5, 5)
            self.assertEqual(m.pc[1], want, x)
        with self.assertRaises(K.Refusal):
            m.op_if_not_constant(code, 0, 1, 0, 5, 0x01000005)
        lib = m.lib
        # no try chain: c_grade_ex.esp-style `set_all(0,P,H,N,M):-!;
        # set_all(C,...) :- ..., set_all(C-1,...);` (p_buf4.esp:98-102),
        # array_index_buffer set_all/5 @18a `ca 00 00 01`, integer 0,
        # `27 00 00 00`, `f0`.  set_all_at(B, 2) on a 3 x 4 buffer sets
        # element 2 of every row (p_buf4.esp:41-42)
        cid = 'paragraph##array_index_buffer'
        m.reset()
        b = K.make_instance(m, cid)
        co = lib.build(cid)
        rows = [K.Vec([0] * 4, heap=True) for _ in range(3)]
        b.slots[lib.slot_number(co, 'instance', 'root')] = K.Vec(rows, heap=True)
        b.slots[lib.slot_number(co, 'instance', 'size')] = 3
        self.assertEqual(len(send(m, b, 'set_all_at', 2)), 1)
        self.assertEqual([repr(K.resolve(r)) for r in rows], ['{0,0,1,0}'] * 3)
        # with a try chain: h draw_string/6 @122 (h.esp:189-190
        # `draw_string(nil,X,Y,List,List,Win):-!; draw_string(S,...) :-
        # type_check(S,S1),!, Font = Win!font, ...`).  nil and an unbound
        # first argument take clause 1 (List = List2, S bound to nil); a
        # string jumps to clause 2, which reads the unbound window's font
        cid = 'paragraph##h'
        code = m.code(cid)
        (p,) = [p for p in lib.templates[cid].locals if (p.name, p.arity) == ('draw_string', 6)]
        for s in (K.Atom('nil'), K.Var()):
            L, L2 = K.Var(), K.Var()
            args = [s, 1, 2, L, L2, K.Var()]
            sols = [(K.resolve(L) is K.resolve(L2), K.resolve(args[0])) for _ in m.solve((code, p.offset), args)]
            self.assertEqual(sols, [(True, K.Atom('nil'))], s)
        with self.assertRaises(K.Refusal) as e:
            list(m.solve((code, p.offset), [K.Str('ab'), 1, 2, K.Var(), K.Var(), K.Var()]))
        self.assertEqual(e.exception.cause, 'unbound receiver')

    def test_step3d_cells(self):
        # step 3d's rows on their witness operands, handlers alone
        # (2026-11-24)
        m = machine()
        A = K.Atom
        # dict_io.esp:55 `6e 00 03 00` (L over V) and BCMSEQUEN.ESP:432
        # `6e 03 00 00` (V in X3, the list out in A0 over the tail)
        for ops in ((0, 3, 0), (3, 0, 0), (0, 1, 2)):
            m.reset()
            m.x[ops[0]], m.x[ops[1]] = K.Vec([A('a'), 2, A('c')]), K.NIL
            m.op_vector_to_list(None, 0, *ops, None)
            self.assertEqual(repr(m.x[ops[2]]), '[a,2,c]', ops)
        m.reset()
        m.x[0], m.x[3] = K.Vec([]), K.NIL
        m.op_vector_to_list(None, 0, 0, 3, 0, None)
        self.assertIs(m.x[0], K.NIL)
        # unwitnessed: a tail other than [] (vrm.esp:595's `_`), a heap vector
        for v, t in ((K.Vec([1]), K.Var()), (K.Vec([1], heap=True), K.NIL)):
            m.reset()
            m.x[0], m.x[3] = v, t
            with self.assertRaises(K.Refusal):
                m.op_vector_to_list(None, 0, 0, 3, 0, None)
        # p_tgraph.esp:299 `b4 03`, four unify_value_p, then `34 01 00 02`
        # + `integer 03000000`: set_subvector(Hv,0,4,{X,Y,W,H})
        m.reset()
        m.op_put_vector_4(None, 0, 3, 0, 0, None)
        v4 = m.x[3]
        self.assertEqual(len(v4.args), 4)
        for i, e in enumerate((10, 20, 30, 40)):
            m.unify(v4.args[i], e)
        # the operand cell after the instruction (only `cells` is read)
        code = types.SimpleNamespace(id='test', cells={1: (1, 0x00, 0, 0x03000000)})
        m.x[0], m.x[1], m.x[2] = 0, K.Vec([0] * 4, heap=True), 4
        m.pc = 'here'
        m.op_set_subvector(code, 0, 1, 0, 2, None)
        self.assertEqual([K.deref(e) for e in m.x[1].args], [10, 20, 30, 40])
        # typewin.esp:259 `b0 01`: {} in A1
        m.reset()
        m.op_put_vector_0(None, 0, 1, 0, 0, None)
        self.assertEqual((type(m.x[1]), m.x[1].args, m.x[1].heap), (K.Vec, [], False))
        # bar_v.esp:384 `45 00 01 06` and as_pred.esp:254 `46 04 0b 00`:
        # the result in another register than the operand
        m.reset()
        m.x[0], m.x[4] = 7, 30
        m.op_add_constant(None, 0, 0, 1, 6, None)
        m.op_subtract_constant(None, 0, 4, 11, 0, None)
        self.assertEqual((m.x[0], m.x[6], m.x[4]), (19, 8, 30))
        # p_tgraph.esp:70-72 `a1 00 02`: one new variable in A0 and X2
        m.reset()
        m.op_put_variable_t(None, 0, 0, 2, 0, None)
        self.assertIs(m.x[0], m.x[2])
        self.assertIsInstance(m.x[0], K.Var)

    def test_string_cells(self):
        # the string rows' witness operands, run on the handlers alone:
        # view_select_menu change/3 `a7 00 00 03`, `a7 01 00 10`,
        # `1c 04 00 01` (new_string(S,3,16), S out in A4); then
        # set_string_element / string_element / string on it
        m = machine()
        m.reset()
        m.x[0], m.x[1] = 3, 16
        m.op_new_string(None, 0, 4, 0, 1, None)
        s = m.x[4]
        self.assertEqual((type(s), s.type, s.codes(), m.x[1]), (K.Str, 16, [0, 0, 0], 16))
        m.x[2], m.x[3] = 1, 0x2121
        m.op_set_string_element(None, 0, 4, 2, 3, None)
        m.op_string_element(None, 0, 4, 2, 5, None)
        m.op_string(None, 0, 4, 6, 7, None)
        self.assertEqual((s.codes(), m.x[5], m.x[6], m.x[7]), ([0, 0x2121, 0], 0x2121, 3, 16))

    def test_step3c_cells(self):
        # the step 3c rows on their witness operands, handlers alone
        # (2026-11-24).  A test that fails leaves pc None (empty stack)
        m = machine()
        # h.esp:186 `40 01 00 01`: A1 := A1 + A0
        m.reset()
        m.x[0], m.x[1] = 5, 7
        m.op_add(None, 0, 1, 0, 1, None)
        self.assertEqual(m.x[1], 12)
        m.op_add(None, 0, 1, 0, 2, None)    # R != A: witnessed in step 3e
        self.assertEqual(m.x[2], 17)
        # `01 01`, `10 00`, `16 00`: type tests fail, never refuse
        for f, x, want in ((m.op_integer, 3, True), (m.op_integer, K.Var(), False),
                           (m.op_integer, K.Atom('a'), False), (m.op_unbound, K.Var(), True),
                           (m.op_unbound, 3, False), (m.op_bound, 3, True),
                           (m.op_bound, K.Var(), False)):
            m.reset()
            m.pc = 'here'
            m.x[0] = x
            f(None, 0, 0, 0, 0, None)
            self.assertEqual(m.pc is not None, want, (f.__name__, x))
        # `06 00 04`: stack_vector(SV, Size) on a stack vector, not a heap one
        for v, want in ((K.Vec([1, 2, 3]), 3), (K.Vec([1, 2], heap=True), None)):
            m.reset()
            m.pc = 'here'
            m.x[0] = v
            m.op_stack_vector(None, 0, 0, 4, 0, None)
            self.assertEqual(m.x[4] if m.pc is not None else None, want)
        # `68 04 01`, `33 00 02 09`
        m.reset()
        m.pc = 'here'
        m.x[4], m.x[1] = K.Str('ab'), K.Str('ab')
        m.op_equal_string(None, 0, 4, 1, 0, None)
        self.assertIsNotNone(m.pc)
        m.x[0], m.x[2] = K.Str('abcdef'), 4
        m.op_string_tail(None, 0, 0, 2, 9, None)
        self.assertEqual(repr(m.x[9]), "string#'ef'")
        m.pc = 'here'
        m.x[1] = K.Str('ac')
        m.op_equal_string(None, 0, 4, 1, 0, None)
        self.assertIsNone(m.pc)


class StringIdentity(unittest.TestCase):
    """Strings unify only with the same stored string (2026-11-25): TM-388
    PDF p79 (folio 67), 'abc'='abc', == and =:= fail, equal_string/2
    succeeds; p117-119 Table 4-3; TM-115 PDF p97.  string/3 is a type test
    (TR-044 App. A.2 PDF p39)."""

    def test_unify_and_identical(self):
        m = machine()
        a, b = K.Str('abc'), K.Str('abc')
        m.reset()
        self.assertFalse(m.unify(a, b))
        self.assertTrue(m.unify(a, a))
        v = K.Var()
        self.assertTrue(m.unify(v, a))
        self.assertTrue(m.unify(v, a))
        self.assertFalse(m.unify(v, b))
        m.x[0], m.x[1], m.x[2] = a, b, a
        self.assertFalse(m.identical(0, 1))
        self.assertTrue(m.identical(0, 2))
        m.pc = 'here'
        m.op_equal_string(None, 0, 0, 1, 0, None)
        self.assertIsNotNone(m.pc)
        # a structure holding them: element-wise, so the same rule
        self.assertFalse(m.unify(K.Vec([a]), K.Vec([b])))
        self.assertTrue(m.unify(K.Vec([a]), K.Vec([a])))

    def test_string_is_a_type_test(self):
        m = machine()
        for x, ok in ((K.Str('ab'), True), (K.Var(), False), (3, False), (K.Atom('ab'), False)):
            m.reset()
            m.pc = 'here'
            m.x[0] = x
            m.op_string(None, 0, 0, 1, 2, None)
            self.assertEqual(m.pc is not None, ok, x)
            if ok:
                self.assertEqual(m.x[1], 2)


class Convert(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = K.convert_report(machine())

    def test_against_pimos(self):
        st = {}
        for name, _f, _p, s in self.r['rows']:
            st.setdefault(s, []).append(name)
        self.assertEqual(len(st['equal']), 96)
        self.assertEqual(st['fep only'], ['all_device_end', 'creation_fail', 'device_end',
                                          'remote_echo_check'])
        self.assertEqual(st['pimos only'], ['deleted', 'listing', 'next_filename', 'packet_continued',
                                            'packet_last', 'remote_socket', 'symbol', 'window'])
        self.assertNotIn('differ', st)
        self.assertEqual(len(self.r['by_code']), 95)
        self.assertEqual(len(self.r['by_name']), 100)

    def test_cut(self):
        # every clause ends in a cut: one answer per code, earlier clause wins
        self.assertEqual(self.r['by_code'][3], ['control_c'])
        self.assertEqual(self.r['by_name']['attention'], [3])
        self.assertEqual(self.r['by_name']['euc'], [1])
        self.assertEqual(self.r['by_code'][1], ['normal'])
        self.assertEqual(self.r['shadowed'], ['attention', 'euc', 'jis', 'jiskanji', 'sjis'])
        self.assertEqual(self.r['both_unbound'], [])


class Paragraph(unittest.TestCase):
    def test_predicate_num_switch_icon(self):
        # p_itool.esp get_code: X=X0-Icon!x, Y=Y0-Icon!y; p_icon.esp code:
        # Y =< Icon!height/2 (height := 56) -> inc_predicate_num, else dec
        m = machine()
        cid = 'paragraph##predicate_num_switch_icon'
        (sol,) = K.call_class_method(m, cid, 'create', [100, 200, K.Var()])
        icon = sol[2]
        self.assertIsInstance(icon, K.Instance)
        got = {y0: send(m, icon, 'get_code', 105, y0, K.Var())[0][2].name
               for y0 in (210, 228, 229, 240)}
        self.assertEqual(got, {210: 'inc_predicate_num', 228: 'inc_predicate_num',
                               229: 'dec_predicate_num', 240: 'dec_predicate_num'})

    def test_list_index_buffer(self):
        m = machine()
        (sol,) = K.call_class_method(m, 'paragraph##list_index_buffer', 'create', [K.Var()])
        b = sol[0]
        V = K.Var
        self.assertEqual(len(send(m, b, 'clear')), 1)
        send(m, b, 'add_last', A('a'), A('ka'))
        send(m, b, 'add_last', A('b'), A('kb'))
        send(m, b, 'add_first', A('c'), A('kc'))
        self.assertEqual(send(m, b, 'count', V()), [[3]])
        self.assertEqual(repr(send(m, b, 'get_contents', V())), '[[[c,a,b]]]')
        self.assertEqual(repr(send(m, b, 'get_contents_with_key', V())),
                         '[[[{c,kc},{a,ka},{b,kb}]]]')
        self.assertEqual(repr(send(m, b, 'search', A('kb'), V())), '[[kb, b]]')
        self.assertEqual(repr(send(m, b, 'search_num', A('kb'), V(), V())), '[[kb, b, 3]]')
        self.assertEqual(repr(send(m, b, 'search', V())), '[[kc]]')
        self.assertEqual(len(send(m, b, 'remove', A('ka'))), 1)
        self.assertEqual(send(m, b, 'remove', A('ka')), [])
        self.assertEqual(send(m, b, 'count', V()), [[2]])
        self.assertEqual(repr(send(m, b, 'get_contents', V())), '[[[c,b]]]')
        self.assertEqual(repr(send(m, b, 'get_partial_contents', 1, 5, V())), '[[1, 5, [{b,kb}]]]')
        self.assertEqual(repr(send(m, b, 'get_partial_contents', 5, 5, V())), '[[5, 5, []]]')
        self.assertEqual(repr(send(m, b, 'remove_num', A('kb'), V())), '[[kb, 2]]')

    def test_two_primaries(self):
        # TM-388 §3.4: the primaries are alternatives.  scroll_bottom_icon's
        # own :code(_,_,_,scroll_bottom):-! and, from its nature
        # predicate_bottom_icon, :code(Icon,X,Y,Code):- Code=bottom_predicate
        # (p_icon2.esp).  The cut is local to the first primary.
        m = machine()
        m.reset()
        icon = K.new_instance(m.lib, 'paragraph##scroll_bottom_icon')
        got = {}
        for code in (K.Var(), A('bottom_predicate'), A('scroll_bottom'), A('other')):
            got[repr(code) if not isinstance(code, K.Var) else '_'] = [
                repr(s[2]) for s in send(m, icon, 'code', 0, 0, code)]
        self.assertEqual(got, {'_': ['scroll_bottom', 'bottom_predicate'],
                               'bottom_predicate': ['bottom_predicate'],
                               'scroll_bottom': ['scroll_bottom'], 'other': []})

    def test_simpos_refusal(self):
        # time_graph_window:go/1 sends :create/3 to itself; create/3 is not
        # in the held classes, and the class has simpos## ancestors
        m = machine()
        with self.assertRaises(K.Refusal) as e:
            K.call_class_method(m, 'paragraph##time_graph_window', 'go', [])
        self.assertEqual(e.exception.cause, 'simpos')
        self.assertIn('paragraph##time_graph_window:create/3', e.exception.detail)
        self.assertIn('simpos##inferior_window', e.exception.detail)

    def test_version_skew(self):
        m = machine()
        (sol,) = K.call_class_method(m, 'paragraph##paragraph_version', 'get_version', [K.Var()])
        self.assertEqual(sol[0], K.Str('3500'))     # version.esp: "3200"


class SlotInit(unittest.TestCase):
    """new/2 runs slot-initialisation predicates (TM-388 §3.5 pp.49-50).
    Held code, package kappa loaded alone, against its held source."""

    @classmethod
    def setUpClass(cls):
        cls.m = kappa_machine()

    def new(self, cid):
        m = self.m
        sols = []
        for _ in m.solve_send(K.ClassRef(cid), 'new', [K.Var(), K.ClassRef(cid)]):
            sols.append(K.resolve(m.x[0]))
        self.assertEqual(len(sols), 1, cid)
        inst = sols[0]
        co = m.lib.build(cid)
        return {e.name: v for e, v in zip(co.instance_slots, inst.slots)}

    def test_arity_one(self):
        # MEASURED: every slot-initialisation predicate (kind 0x22/0x32) of
        # the eleven packages has arity 1: the value, no receiver
        lib = K.LB.Librarian()
        lib.load_held()
        kinds = {}
        for t in lib.templates.values():
            for p in t.preds():
                if p is not None and p.kind in (0x22, 0x32):
                    kinds[(p.kind, p.arity)] = kinds.get((p.kind, p.arity), 0) + 1
        self.assertEqual(kinds, {(0x22, 1): 33, (0x32, 1): 391})

    def test_hash_table(self):
        # KP_MDMTBL.ESP: ( table := Table :- new_heap_vector(Table,128) )
        s = self.new('kappa##kappaMDM_hash_table')
        t = s['table']
        self.assertIsInstance(t, K.Vec)
        self.assertTrue(t.heap)
        self.assertEqual(t.args, [0] * 128)

    def test_nested_new(self):
        # KP_MDMAR.ESP: (work_hash1 := HT :- :create(#kappaMDM_hash_table,HT)),
        # (work_hash2 := ...same...), access_right_table,
        # (faot := FAOT :- new_heap_vector(FAOT,@max_faot_entry+1)), and
        # KP_MDM.MAC @max_faot_entry => 20.  create/2 (:new(Class,OBJ)) runs
        # the hash table's own initialiser: two distinct tables.
        s = self.new('kappa##kappaMDM_access_right')
        h1, h2 = s['work_hash1'], s['work_hash2']
        for h in (h1, h2):
            self.assertIsInstance(h, K.Instance)
            self.assertEqual(h.cid, 'kappa##kappaMDM_hash_table')
            self.assertEqual(h.slots[0].args, [0] * 128)
        self.assertIsNot(h1, h2)
        self.assertIsNot(h1.slots[0], h2.slots[0])
        self.assertEqual(s['faot'].args, [0] * 21)
        self.assertEqual(s['access_right_table'], 0)

    def test_two_goals(self):
        # KP_TBOSRUC.ESP: (ruc_table := RUCT :- new_heap_vector(RUCT,
        # @sdb_ruc_table_max_entry*2+1), set_vector_element(RUCT,0,1)), and
        # KAPPATBO.MAC @sdb_ruc_table_max_entry => 10
        s = self.new('kappa##kappaTBO_SDB_RUC_control')
        self.assertEqual(s['ruc_table'].args, [1] + [0] * 20)
        self.assertEqual((s['dbo'], s['bfm'], s['rct_lpn']), (0, 0, 0))


    def test_slot_is_class(self):
        # `slot is Class` stores a new instance (TM-388 p.49, (3)), made by
        # new/2, which runs that class's own initialisers.  HLCSELECT.ESP:
        # component ..., search_info_tree is kappaHLC_search_information_tree,
        # practice is kappaHLC_selection_practice; HLCSELSIT.ESP: attribute
        # ..., sit_hv_table is kappaHLC_SIT_HV_table, ...
        s = self.new('kappa##kappaHLC_selection')
        tree = s['kappa##kappaHLC_selection$search_info_tree']
        self.assertEqual(tree.cid, 'kappa##kappaHLC_search_information_tree')
        self.assertEqual(s['kappa##kappaHLC_selection$practice'].cid,
                         'kappa##kappaHLC_selection_practice')
        self.assertEqual(repr(s['kappa##kappaHLC_selection$supervisor']), 'nil')
        co = self.m.lib.build(tree.cid)
        t = {e.name: v for e, v in zip(co.instance_slots, tree.slots)}
        self.assertEqual(t['sit_hv_table'].cid, 'kappa##kappaHLC_SIT_HV_table')


class Step3eRows(unittest.TestCase):
    """Step 3e's rows (2026-11-24): blt 9a/9b, pmi b1/b5/b6/b7, blt 50/51/
    54/55, and R != A for blt 40 and 49 (psi/kl0_opcodes.tsv), on held code
    whose source is held where one runs, else on the handler."""

    def cell(self):
        return types.SimpleNamespace(id='test', cells={}, t=types.SimpleNamespace(symbols=[]))

    def local(self, m, cid, name, regs):
        code = m.code(cid)
        ps = {(p.name, p.arity): p for p in m.lib.templates[cid].locals}
        out = []
        for _ in m.solve((code, ps[(name, len(regs))].offset), regs):
            out.append(K.resolve(regs[-1]))
        return out

    def test_interrupt_brackets(self):
        # blt 9a/9b are no-ops here (no interrupts are modelled): each goes
        # on to the next cell; pimfep_message_log log/2 (the 9a at @1f,
        # then its 9b) now runs to one solution
        m = machine()
        code = self.cell()
        for op in (m.op_inhibit_interrupt, m.op_allow_interrupt):
            m.reset()
            op(code, 7, 0, 0, 0, 0)
            self.assertEqual(m.pc[1], 8)
        m.reset()
        self.assertEqual(len(K.call_class_method(m, 'pimfep##pimfep_message_log', 'log', [K.Var()])), 1)

    def test_vector_puts(self):
        # pmi b1 on held code: HLCAPRSUB.ESP:425-427 make_nest_vector(2, a, F)
        # gives F = {{a}}
        km = kappa_machine()
        km.reset()
        (f,) = self.local(km, 'kappa##kappaHLC_projection_subschema_analyzer', 'make_nest_vector',
                          [2, A('a'), K.Var()])
        self.assertEqual(repr(f), '{{a}}')
        # b5, b6, b7 on the handler: a vector of n new elements in A_A, the
        # element pointer at its first element; b7 with A != 0 or a second
        # byte refuses
        m = machine()
        code = self.cell()
        for op, a, b, c, n in ((m.op_put_vector_1, 2, 0, 0, 1), (m.op_put_vector_5, 1, 0, 0, 5),
                               (m.op_put_vector_6, 1, 0, 0, 6), (m.op_put_vector_n, 0, 0, 12, 12),
                               (m.op_put_vector_n, 1, 0, 9, 9)):
            m.reset()
            op(code, 0, a, b, c, (a << 16) | (b << 8) | c)
            t = K.deref(m.x[a])
            self.assertIsInstance(t, K.Vec)
            self.assertEqual((len(t.args), t.heap, m.S[1], m.pc[1]), (n, False, 0, 1))
            self.assertIs(m.S[0], t.args)
        for a, b in ((0, 1), (1, 1)):
            with self.assertRaises(K.Refusal):
                m.op_put_vector_n(code, 0, a, b, 7, (a << 16) | (b << 8) | 7)
        # step 3f: b7 with A != 0, the witness's cells (KP_MDM.ESP:89
        # `:set_up(DBO,OBJuser,{MS_max,...,IHN})`, nine elements into A1)
        t = km.lib.templates['kappa##kappaMDM_manager']
        cells = {c[0]: c for p in t.preds() if p.name == 'set_up' and p.arity == 2 for c in p.cells}
        self.assertEqual(cells[0xe6][3], 0xb7010009)
        self.assertEqual([cells[o][3] >> 24 for o in range(0xe7, 0xf0)], [0x43] * 9)
        # @f2: a selector cell of arity 3 (set_up/3, the send at @f1)
        self.assertEqual(cells[0xf2][1:3], (1, 3))
        self.assertEqual(K.Code(km.lib, t).sym(cells[0xf2][3]), 'set_up')

    def test_bit_operations(self):
        km = kappa_machine()
        km.reset()
        s = K.Str('')
        s.set_codes([0x0001, 0x0203, 0x7fff, 0x8000, 0x0005])
        # shift_left and or on held code: CONVERTER.ESP:41-45 get_integer
        # is (H << 16) | L of two string elements
        got = [K.call_class_method(km, 'kappa##kappa_converter', 'get_integer', [s, i, K.Var()])[0][2]
               for i in (0, 1)]
        self.assertEqual(got, [0x00010203, 0x02037fff])
        # 0x8000 << 16 does not fit below 2**31: refused, not wrapped (the
        # refusal is shift_left's, not string_element's)
        with self.assertRaises(K.Refusal) as e:
            K.call_class_method(km, 'kappa##kappa_converter', 'get_integer', [s, 3, K.Var()])
        self.assertTrue(e.exception.detail.startswith('shift_left 32768 by 16'), e.exception.detail)
        # and on held code: TERMCODE.ESP:83-89 `( and(Count,1,0),!, Result =
        # Count ; Result = Count + 1 )`, $or$9/2
        self.assertEqual([self.local(km, 'kappa##term_code', '$or$9', [n, K.Var()]) for n in (4, 5)],
                         [[4], [6]])
        # shift_right on the handler (KP_TIMER.ESP:45 `55 00 01 00`), R != X
        m = machine()
        code = self.cell()
        m.reset()
        m.x[0], m.x[1] = 0x50000, 16
        m.op_shift_right(code, 0, 0, 1, 2, 0x000102)
        self.assertEqual((m.x[2], m.x[0]), (5, 0x50000))
        m.x[0], m.x[1] = 0b1100, 0b1010
        m.op_and(code, 0, 0, 1, 2, 0)
        m.op_or(code, 0, 0, 1, 3, 0)
        self.assertEqual((m.x[2], m.x[3]), (0b1000, 0b1110))
        for op, x, y in ((m.op_shift_right, -8, 1), (m.op_shift_left, 1, 32), (m.op_and, -1, 1),
                         (m.op_or, 1, -1)):
            m.x[0], m.x[1] = x, y
            with self.assertRaises(K.Refusal):
                op(code, 0, 0, 1, 2, 0)

    def test_result_register(self):
        # R != A for divide_constant (c_grade_ex.esp:26 `49 00 0a 07`) and
        # add (p_wwin.esp:420 `40 00 01 01`): the result lands in A_R, A_A
        # keeps its value
        m = machine()
        code = self.cell()
        m.reset()
        m.x[0] = 37
        m.op_divide_constant(code, 0, 0, 10, 7, 0x000a07)
        self.assertEqual((m.x[7], m.x[0]), (3, 37))
        m.x[0], m.x[1] = 5, 9
        m.op_add(code, 0, 0, 1, 1, 0x000101)
        self.assertEqual((m.x[1], m.x[0]), (14, 5))
        # V != N for new_heap_vector (FMT_CONV.ESP:13-16 `19 02 04 00`):
        # the vector lands in A_V, A_N keeps the length
        m.x[4] = 3
        m.op_new_heap_vector(code, 0, 2, 4, 0, 0x020400)
        self.assertEqual((len(m.x[2].args), m.x[2].heap, m.x[4]), (3, True, 3))
        # step 3g: R != A for multiply_constant (p_hwin.esp:233
        # `Y=<(Height*2)`, `48 00 02 03`): A3 := A0 * 2, A0 keeps Height
        m.x[0], m.x[3] = 7, 99
        m.op_multiply_constant(code, 0, 0, 2, 3, 0x000203)
        self.assertEqual((m.x[3], m.x[0]), (14, 7))
        # the witness's cells: the two products into the temporary A3, each
        # compared with Y (A1) by not_less_than(A3, A1)
        t = machine().lib.templates['paragraph##scroll_bar_icon']
        cells = {c[0]: c for p in t.preds() if p.name == '$or$0' and p.arity == 3 for c in p.cells}
        self.assertEqual([cells[o][3] for o in (0x282, 0x283, 0x288, 0x289)],
                         [0x48000203, 0x67030100, 0x48000303, 0x67030100])
        cells = {c[0]: c for p in t.preds() if p.name == 'code' and p.arity == 4 for c in p.cells}
        self.assertEqual([cells[o][3] for o in (0x14, 0x15)], [0x27030000, 0x49000400])


class Step3eCensus(unittest.TestCase):
    """Step 3e's census semantics (2026-11-24): slot constants named as
    receivers, and the uncaught :raise(#undefined_method, ...)."""

    def test_slot_constant(self):
        # an integer slot's template constant is marked; arithmetic on it
        # gives plain ints; a send to it is refused with its own cause, a
        # send to any other integer as before
        m = machine()
        cid = 'paragraph##array_index_buffer'
        m.reset()
        b = K.make_instance(m, cid)
        co = m.lib.build(cid)
        size = b.slots[m.lib.slot_number(co, 'instance', 'size')]
        self.assertIsInstance(size, K.SlotConstant)
        self.assertEqual(size, 0)
        self.assertIs(type(size + 1), int)
        for recv, cause in ((size, 'receiver a slot constant'), (0, 'receiver not an object')):
            with self.assertRaises(K.Refusal) as e:
                m.dispatch(recv, 'put', 2)
            self.assertEqual(e.exception.cause, cause)

    def test_uncaught_exception(self):
        # scsi_low_if's class reset/1 raises unless overridden: cmt does not
        # override it, so the send ends in an uncaught exception whose
        # information is {Class, undefined_method, Class, {Method, Args, _}}
        m = machine()
        m.reset()
        with self.assertRaises(K.Raised) as e:
            K.call_class_method(m, 'pimscsi##cmt', 'reset', [])
        info = e.exception.info
        self.assertEqual(repr(info.args[1]), 'undefined_method')
        self.assertEqual(repr(info.args[3].args[0]), 'reset')
        rows = K.census_of(m, ['pimscsi##cmt'])
        out = dict((r[2], r[3]) for r in rows if r[1] == 'class')
        self.assertEqual((out['reset/1'], out['initialize/1']), ('exception', 'exception'))


class Step3gSwitches(unittest.TestCase):
    """pmi c6 switch_on_term, ce switch_on_vector, c3 retry, c1 trust, ff
    jump and the cd03/cd04 tables (step 3g), on held code beside its
    held source.  Each first-argument type is run, and the clauses it
    reaches are the ones the source says can match."""

    def run_local(self, m, cid, name, n, off, args):
        code = m.code(cid)
        (p,) = [p for p in m.lib.templates[cid].locals if (p.name, p.arity, p.offset) == (name, n, off)]
        m.reset()
        return [[K.resolve(a) for a in args] for _ in m.solve((code, p.offset), args)]

    def test_get_bfs_list_only(self):
        # RDMSOPE.ESP:285-291 `get_BFS_list_only([],[]):-!;
        # get_BFS_list_only([{_,Buffer_string}|Info_list],[Buffer_string|
        # BFS_list]):-!, ...; get_BFS_list_only(end,end);`, compiled into
        # kappaRDM_manager @6b7 (c6, cc [], cc end, fe, ff, e4 chain)
        m = kappa_machine()
        cid = 'kappa##kappaRDM_manager'
        run = lambda a0: self.run_local(m, cid, 'get_BFS_list_only', 2, 0x6b7, [a0, K.Var()])  # noqa: E731
        self.assertEqual(repr(run(K.NIL)), '[[[], []]]')
        self.assertEqual(repr(run(A('end'))), '[[end, end]]')
        self.assertEqual(run(A('foo')), [])            # atom, no clause: the cc chain's fe
        self.assertEqual(run(K.Vec([A('a')])), [])     # vector: ff to fe
        self.assertEqual(repr(run(K.Var())), '[[[], []]]')   # the e4 chain, clause 1 cuts
        # a list reaches clause 2 (@6c5 2b, past its e2).  Until step 3i it
        # stopped at the unrowed pmi 3b @6c9; now 3b and the recursive
        # pmi 6c @6cd (to this c6) run it to the end
        self.assertEqual(repr(run(K.Cons(K.Vec([1, A('s1')]), K.NIL))), '[[[{1,s1}], [s1]]]')
        two = K.Cons(K.Vec([1, A('s1')]), K.Cons(K.Vec([2, A('s2')]), A('end')))
        self.assertEqual(repr(run(two)), '[[[{1,s1},{2,s2}|end], [s1,s2|end]]]')
        for x in (5, K.Str('ab')):
            with self.assertRaises(K.Refusal) as e:
                run(x)
            self.assertEqual(e.exception.cause, 'operand')
            self.assertIn('pmi c6 on', str(e.exception))

    def test_get_tap_type(self):
        # a `cc` chain on ce's register: kappa2 KP_MDMSCT.ESP:316-321
        # `get_tap_type(primitive,tap_primitive):-!; ...
        # get_tap_type(primitive(table),tap_primitive_table):-!;
        # get_tap_type(table(id),tap_table_id):-!; ...`, compiled into
        # kappaMDM_schema_table @1c2: c6, ce 00 02 @1ce, `cc 02 ..
        # primitive/2` -> @1e5, `cc 02 .. table/2` -> @1e9, fe
        m = kappa_machine()
        cid = 'kappa##kappaMDM_schema_table'

        def run(a0):
            return [repr(r[1]) for r in self.run_local(m, cid, 'get_tap_type', 2, 0x1c2, [a0, K.Var()])]
        self.assertEqual(run(A('primitive')), ['tap_primitive'])
        self.assertEqual(run(K.Vec([A('primitive'), A('table')])), ['tap_primitive_table'])
        self.assertEqual(run(K.Vec([A('table'), A('id')])), ['tap_table_id'])
        self.assertEqual(run(K.Vec([A('table'), A('x')])), [])
        self.assertEqual(run(K.Vec([A('foo'), 1])), [])
        # N counts: a 3-vector's key primitive/3 is not primitive/2
        self.assertEqual(run(K.Vec([A('primitive'), A('table'), A('z')])), [])

    def test_make_com(self):
        # p_MAIN.esp:479-689: twenty atom clauses (cd00 @471), seventeen
        # 3-vector clauses (ce @4bb, cd03 @4bd, the c3 chain @501, ff @512),
        # then two `make_com(Mes,code(window,Com),VS)` catch-alls (:663, :689)
        m = machine()
        cid = 'paragraph##view_selector'

        def first(a0):
            out = []
            code = m.code(cid)
            (p,) = [p for p in m.lib.templates[cid].locals if (p.name, p.arity) == ('make_com', 3)]
            m.reset()
            args = [a0, K.Var(), K.Var()]
            for _ in m.solve((code, p.offset), args):
                out.append([K.resolve(a) for a in args[:2]])
                break
            return repr(out)
        self.assertEqual(first(A('exit')), '[[exit, {code,exit,nil}]]')           # :479
        self.assertEqual(first(K.Vec([A('kill'), 1, 2])), '[[{kill,1,2}, {code,window,{kill,1,2}}]]')  # :579
        # element 0 unbound: the c3 chain, kill first in source order
        self.assertEqual(first(K.Vec([K.Var(), 1, 2])), '[[{kill,1,2}, {code,window,{kill,1,2}}]]')
        # an atom with no clause: the table misses to the catch-alls, whose
        # `Mes={Code,Wid,Gid}` fails
        self.assertEqual(first(A('zzz')), '[]')
        # a 3-vector with no clause: the catch-all :663 runs its body,
        # check_when_where(VS,Gid) on the unbound VS
        with self.assertRaises(K.Refusal) as e:
            first(K.Vec([A('zzz'), 1, 2]))
        self.assertEqual(e.exception.cause, 'unbound receiver')

    def test_receiver_send(self):
        # receiver.esp:38-686 (paragraph##receiver send/3 @11c: c6, cc
        # read_code, ff, ce 00 04, the cd04 table keyed Name/N)
        m = machine()
        cid = 'paragraph##receiver'
        co = m.lib.build(cid)

        def send3(msg):
            m.reset()
            o = K.Instance(cid, [K.Var() for _ in co.instance_slots])
            res = K.Var()
            for _ in m.solve_send(o, 'send', [msg, res, o]):
                sl = {e.name.split('$')[-1]: K.resolve(v) for e, v in zip(co.instance_slots, o.slots)}
                return repr(K.resolve(res)), sl
            return None, None
        r, sl = send3(K.Vec([A('goal_name'), K.Str('g')]))      # :54
        self.assertEqual((r, repr(sl['goal_name'])), ("string#'normal'", "string#'g'"))
        r, sl = send3(K.Vec([A('view_mode'), A('act')]))         # :46
        self.assertEqual((r, sl['view_mode'], sl['view']), ("string#'normal'", A('act'), A('pe_view')))
        r, sl = send3(K.Vec([A('view_mode'), A('other')]))       # :50, after :46 fails
        self.assertEqual((r, sl['view_mode'], isinstance(sl['view'], K.Var)), ("string#'normal'", A('other'), True))
        # the catch-all :686 for a vector key not in the table, an atom
        # other than read_code (ff), and a list (c6 lo16)
        for msg in (K.Vec([A('foo'), 1, 2]), A('zzz'), K.Cons(1, K.NIL)):
            self.assertEqual(send3(msg)[0], "string#'abnormal'", msg)
        # unbound, and element 0 unbound: both reach clause 1, color(Code)
        # (:38), whose first goal is a SIMPOS send
        for msg in (K.Var(), K.Vec([K.Var(), A('act')])):
            with self.assertRaises(K.Refusal) as e:
                send3(msg)
            self.assertIn('get_plane_count', str(e.exception), msg)
        # N counts element 0: the table's three init keys, by the handlers
        code = m.code(cid)
        for vec, want in (([A('init'), A('pe_view'), 1, 2], 0x219), ([A('init'), A('htree_view')], 0x21d),
                          ([A('init'), A('htree_view'), 1, 2, 3], 0x21f)):
            m.reset()
            m.x[0] = K.Vec(vec)
            c = code.cells[0x124]
            m.op_switch_on_vector(code, 0x124, 0, 4, 0, c[3])
            self.assertEqual((m.pc[1], m.x[4]), (0x126, K.Functor('init', len(vec))))
            m.op_hash_constant(code, 0x126, code.cells[0x126])
            self.assertEqual(m.pc[1], want, vec)
        # what the handlers refuse
        for msg in (7, K.Vec([3, 4])):
            with self.assertRaises(K.Refusal) as e:
                send3(msg)
            self.assertEqual(e.exception.cause, 'operand', msg)
        fake = types.SimpleNamespace(id='test', cells={1: (1, 0, 0, 5), 2: (2, 0, 0, 0x60000b)})
        with self.assertRaises(K.Refusal):
            m.op_switch_on_term(fake, 0, 0, 0, 0x1a, 0xc600001a)
        with self.assertRaises(K.Refusal):
            m.op_jump(fake, 0, 1, 0, 2, 0xff010002)


class Step3hRows(unittest.TestCase):
    """pmi 34 and 35 (get_vector_4, get_vector_5), step 3h, run end to end
    on paragraph##receiver send/3, beside receiver.esp:669-681."""

    def send3(self, msg):
        """:send(Obj, Msg, Res) on a receiver whose slots are unbound:
        each init clause's body sends to Obj!d_map, unbound, so it refuses
        there with the body's message in A0 (or Res is returned)."""
        m = machine()
        cid = 'paragraph##receiver'
        co = m.lib.build(cid)
        m.reset()
        o = K.Instance(cid, [K.Var() for _ in co.instance_slots])
        res = K.Var()
        try:
            for _ in m.solve_send(o, 'send', [msg, res, o]):
                return 'result', repr(K.resolve(res))
            return 'failure', None
        except K.Refusal as e:
            return e.cause, repr(K.resolve(m.x[0]))

    def test_get_vector_4(self):
        # :669, :672, :675 `:send(Obj,init(V,PE,Wid),Res):-!, :send(Obj!d_map,
        # init(V,PE,Wid),Res)`: @b2f, @b3f, @b4f `34 00` read the head's
        # 4-vector; the body's `b4 00` rebuilds it
        for view in ('pe_view', 'overall_stack_view', 'stack_view'):
            self.assertEqual(self.send3(K.Vec([A('init'), A(view), 5, 6])),
                             ('unbound receiver', '{init,%s,5,6}' % view))
        # a view no clause names: the init/4 chain fails through, and the
        # catch-all :686 answers "abnormal"
        self.assertEqual(self.send3(K.Vec([A('init'), A('zzz_view'), 5, 6])),
                         ('result', "string#'abnormal'"))

    def test_get_vector_5(self):
        # :680 `:send(Obj,init(htree_view,{Id,Nid},Depth,Wid),Res)`: @b67 `35
        # 00`, then `32 00` on the {Id,Nid} it put in X0
        self.assertEqual(self.send3(K.Vec([A('init'), A('htree_view'), K.Vec([1, 2]), 3, 4])),
                         ('unbound receiver', '{init,htree_view,{1,2},3,4}'))
        # element 2 not a 2-vector: 32 fails, so does the clause
        self.assertEqual(self.send3(K.Vec([A('init'), A('htree_view'), 7, 3, 4])),
                         ('result', "string#'abnormal'"))

    def run_or(self, cid, name, args):
        m = machine()
        code = m.code(cid)
        ps = {(p.name, p.arity): p for p in m.lib.templates[cid].locals}
        try:
            n = sum(1 for _ in m.solve((code, ps[(name, len(args))].offset), args))
            return n, [K.resolve(a) for a in args]
        except K.Refusal as e:
            return e.cause, e.detail.split(' (')[0]

    def test_if_integer(self):
        # blt e1 (step 3h): integer/1 as a test-and-branch.
        # what_manipulator $or$3/2 (p_what.esp:87-89 `(Code==exit,!;
        # integer(Code),!,:select(W,Code); Code==previous_page,!,
        # :previous_page(W); ...`), W unbound: an integer goes on to select/2
        # (@53b), anything else jumps to @53d, the previous_page test
        cid = 'paragraph##what_manipulator'
        self.assertEqual(self.run_or(cid, '$or$3', [A('exit'), K.Var()])[0], 1)
        self.assertEqual(self.run_or(cid, '$or$3', [5, K.Var()]),
                         ('unbound receiver', 'send select/2 to an unbound receiver'))
        self.assertEqual(self.run_or(cid, '$or$3', [A('previous_page'), K.Var()]),
                         ('unbound receiver', 'send previous_page/1 to an unbound receiver'))
        # an unbound Code is not an integer: e1 jumps, and it does not
        # reach select/2
        self.assertNotEqual(self.run_or(cid, '$or$3', [K.Var(), K.Var()])[1:],
                            ('send select/2 to an unbound receiver',))
        # A != 0: view_selector $or$11/5 (p_MAIN.esp:723 `(integer(N),
        # N>Max,!,F1=1,N1=Max;F1=F,N1=N)`, registers F, N, F1, Max, N1): a
        # non-integer N takes F1=F, N1=N (@a2e-a2f); an integer goes on
        # to the unrowed blt f4 (N>Max)
        cid = 'paragraph##view_selector'
        n, r = self.run_or(cid, '$or$11', [A('f'), A('t'), K.Var(), 9, K.Var()])
        self.assertEqual((n, r[2], r[4]), (1, A('f'), A('t')))
        self.assertEqual(self.run_or(cid, '$or$11', [K.Var(), 3, K.Var(), 9, K.Var()]),
                         ('opcode', 'blt f4'))
        m = machine()
        fake = types.SimpleNamespace(id='test', cells={})
        with self.assertRaises(K.Refusal):
            m.op_if_integer(fake, 0, 0, 1, 3, 0)

    def test_nonzero_bytes_refused(self):
        m = machine()
        fake = types.SimpleNamespace(id='test', cells={})
        for op, k in ((m.op_get_vector_4, 4), (m.op_get_vector_5, 5)):
            m.reset()
            m.x[0] = K.Vec([K.Var() for _ in range(k)])
            with self.assertRaises(K.Refusal) as e:
                op(fake, 0, 0, 1, 0, 0)
            self.assertEqual(e.exception.cause, 'operand')
            # A != 0 (receiver set_pred_pool/2 @11d0 `34 01`, h draw_string/6
            # @13d `35 01`): the register named is read
            m.reset()
            m.x[1] = K.Vec([K.Var() for _ in range(k)])
            op(fake, 0, 1, 0, 0, 0)
            self.assertEqual(m.pc, (fake, 1))


class Step3iRows(unittest.TestCase):
    """pmi 3b get_val_var_list and pmi 6c execute_local_switch (step 3i),
    on kappa##kappa_loader local append/3 @90 beside its held source,
    kappa2 utility/tool/LOADER.ESP:118-126:
        append([],[],[]):-!;
        append([],[O|Ol],[O|C]):-!, append([],Ol,C);
        append([D|Dl],O,[D|C]):- append(Dl,O,C);
    Each answer below is the one the source gives."""

    def append(self, *args):
        m = kappa_machine()
        cid = 'kappa##kappa_loader'
        (p,) = [p for p in m.lib.templates[cid].locals if (p.name, p.arity, p.offset) == ('append', 3, 0x90)]
        m.reset()
        return [repr([K.resolve(a) for a in args]) for _ in m.solve((m.code(cid), p.offset), list(args))]

    @staticmethod
    def lst(*xs):
        t = K.NIL
        for x in reversed(xs):
            t = K.Cons(x, t)
        return t

    def test_append(self):
        L, a, b, c = self.lst, A('a'), A('b'), A('c')
        self.assertEqual(self.append(K.NIL, K.NIL, K.Var()), ['[[], [], []]'])
        # clause 3 twice through 6c @94 (c9 list target), then clause 2's
        # 6c @a3 (c9 const target) and clause 1
        self.assertEqual(self.append(L(a, b), L(c), K.Var()), ['[[a,b], [c], [a,b,c]]'])
        self.assertEqual(self.append(K.NIL, L(a, b), K.Var()), ['[[], [a,b], [a,b]]'])
        # 3b unifies the car with X_H: a wrong third argument fails
        self.assertEqual(self.append(L(a), L(b), L(a, b)), ['[[a], [b], [a,b]]'])
        self.assertEqual(self.append(L(a), L(b), L(a, c)), [])
        self.assertEqual(self.append(L(b), L(b), L(a, b)), [])
        # an unbound first argument takes the c9's unbound target (e5 chain)
        self.assertEqual(self.append(K.Var(), K.NIL, L(a)), ['[[a], [], [a]]'])
        self.assertEqual(self.append(A('x'), K.NIL, K.Var()), [])

    def test_atom(self):
        # blt e0 (if_atom) and blt 00 (atom/1), step 3i, on paragraph code
        # beside its source; Step3hRows.run_or runs a local predicate
        run = Step3hRows('test_if_integer').run_or
        sym = 'send simpos##symbolizer:'
        # as_pred.esp:419 `( atom(Atom),! ; integer(Atom),!)`: e0 @1009
        cid = 'paragraph##as_draw_predicate'
        for x, n in ((A('a'), 1), (K.NIL, 1), (5, 1), (K.Str('ab'), 0), (K.Var(), 0)):
            self.assertEqual(run(cid, '$or$26', [x])[0], n, x)
        # as_pred.esp:421-422: an atom goes to get_atom_string/3, an integer
        # to get_number_string/3, anything else fails
        self.assertEqual(run(cid, '$or$27', [A('a'), K.Var()]), ('simpos', sym + 'get_atom_string/3'))
        self.assertEqual(run(cid, '$or$27', [5, K.Var()]), ('simpos', sym + 'get_number_string/3'))
        self.assertEqual(run(cid, '$or$27', [K.Str('ab'), K.Var()])[0], 0)
        # g_window.esp:146-149: e1 then blt 00 @709 on the same register
        cid = 'paragraph##g_window'
        self.assertEqual(run(cid, '$or$12', [A('a'), K.Var()]), ('simpos', sym + 'get_atom_string/3'))
        self.assertEqual(run(cid, '$or$12', [5, K.Var()]), ('simpos', sym + 'get_number_string/3'))
        self.assertEqual(run(cid, '$or$12', [K.Str('ab'), K.Var()])[0], 0)
        # X != 0 (bar2_h.esp:135 @574 `00 02`): the register named is read
        m = machine()
        fake = types.SimpleNamespace(id='test', cells={})
        m.reset()
        m.x[0], m.x[2] = 5, A('x_name_value')
        m.op_atom(fake, 0, 2, 0, 0, 0)
        self.assertEqual(m.pc, (fake, 1))
        with self.assertRaises(K.Refusal):
            m.op_if_atom(fake, 0, 0, 1, 3, 0)

    def test_switch_on_vector_else(self):
        # pmi c8 (step 3i) on kappaHLC_SIT_taker optimum_set_left_set/7 @234
        # (HLCSESITTK.ESP:408-424: clause 1 `@anb`, clause 2 `_`), and the
        # 6c calls into the c8s of BCMGETREC.ESP:124-160 (both clauses a
        # vector), each first-argument type
        m = kappa_machine()

        def at(cid, off, x, op):
            code = m.code(cid)
            w = code.cells[off][3]
            m.reset()
            m.x[0] = x
            op(code, off, (w >> 16) & 255, (w >> 8) & 255, w & 255, w)
            return m.pc[1]
        cid = 'kappa##kappaHLC_SIT_taker'
        sw = m.op_switch_on_vector_else
        self.assertEqual(at(cid, 0x234, K.Var(), sw), 0x23d)                  # e4, both clauses
        self.assertEqual(at(cid, 0x234, K.Vec([A('@'), A('anb')]), sw), 0x236)  # ce
        for x in (A('foo'), 3, K.Cons(A('a'), K.NIL), K.Str('s')):
            self.assertEqual(at(cid, 0x234, x, sw), 0x250, x)                # clause 2
        cid = 'kappa##kappaBCM_get_primitive_record'
        ex = m.op_execute_local_switch
        for off, chain, fail in ((0x5d, 0x135, 0x17c), (0x54, 0x19e, 0x1c6)):
            self.assertEqual(at(cid, off, K.Var(), ex), chain)
            self.assertEqual(at(cid, off, K.Vec([A('t'), 1]), ex), chain)
            self.assertEqual(at(cid, off, A('foo'), ex), fail)
            self.assertEqual(at(cid, off, K.Cons(A('a'), K.NIL), ex), fail)
        with self.assertRaises(K.Refusal):
            sw(types.SimpleNamespace(id='test', cells={1: (0, 0x00, 0, 3)}), 0, 1, 0, 5, 0xc8010005)
        # a non-zero high half in W (no held use) refuses
        m.reset()
        m.x[0] = K.Var()
        with self.assertRaises(K.Refusal):
            sw(types.SimpleNamespace(id='test', cells={1: (0, 0x00, 0, 0x00010003)}), 0, 0, 0, 5, 0xc8000005)

    def test_new_stack_vector(self):
        # blt 1a (step 3i): kappa2 user_if/pb/mcd.esp:112-116 make_term/5
        # (pb_siki_make_cond @a3): new_stack_vector(Cond,3), then each
        # element unified with a constant or an argument; the last clause
        # (no cut in the source) gives Flag = 1
        m = kappa_machine()
        cid = 'kappa##pb_siki_make_cond'
        (p,) = [p for p in m.lib.templates[cid].locals if p.offset == 0xa3]

        def run(op):
            args = [A(op), A('age'), 30, K.Var(), K.Var()]
            m.reset()
            return [repr([K.resolve(a) for a in args][3:]) for _ in m.solve((m.code(cid), p.offset), args)]
        r = run('=')
        self.assertEqual((len(r), r[0]), (2, '[{=,age,30}, 0]'))
        self.assertTrue(r[1].startswith('[_G') and r[1].endswith(', 1]'), r[1])
        self.assertEqual(run('<')[0], '[{<,age,30}, 0]')
        self.assertEqual(len(run('foo')), 1)
        # V != N (KP_BFMOM.ESP:181-185 @93 `1a 02 00 00`): size in A0, vector to A2
        fake = types.SimpleNamespace(id='test', cells={})
        m.reset()
        m.x[0] = 21
        m.op_new_stack_vector(fake, 0, 2, 0, 0, 0)
        v = K.deref(m.x[2])
        self.assertEqual(len(v.args), 21)
        self.assertTrue(all(isinstance(K.deref(e), K.Var) for e in v.args))
        self.assertEqual(m.x[0], 21)
        with self.assertRaises(K.Refusal):
            m.op_new_stack_vector(fake, 0, 2, 0, 1, 0)

    def test_list_to_vector(self):
        # blt 6f (step 3k): list_to_vector(L, ^V, ^Tail), on held code.
        # kappaRDO_check check_list/1 @a4 (ROCHECK.ESP:119-121
        # `list_to_vector(List,_,Tail), Tail == []`): a proper list passes;
        # an improper one fails (its Tail is the terminator: INFERENCE)
        m = kappa_machine()
        cid = 'kappa##kappaRDO_check'
        (p,) = [p for p in m.lib.templates[cid].locals if p.offset == 0xa4]

        def lst(*xs, tail=K.NIL):
            out = tail
            for x in reversed(xs):
                out = K.Cons(x, out)
            return out

        def ok(arg):
            m.reset()
            return len(list(m.solve((m.code(cid), p.offset), [arg])))
        self.assertEqual(ok(lst(A('a'), 1, A('b'))), 1)
        self.assertEqual(ok(lst(A('a'), tail=A('z'))), 0)
        self.assertEqual(ok(lst(A('a'), tail=K.Var())), 0)
        # kappaHLC_ext_selection delete_temp/1 @720-723 (HLCEXTSEL.ESP:
        # 170-173): the vector goes to stack_vector/2, so it is a stack
        # vector; with distinct registers as KP_UPTACC $or$9/2 @6eb `6f 01
        # 02 00`: L from A1, V to A2, Tail to A0
        fake = types.SimpleNamespace(id='test', cells={})
        m.reset()
        e = K.Var()
        m.x[1] = lst(A('x'), e, 7, tail=A('t'))
        m.op_list_to_vector(fake, 0, 1, 2, 0, 0)
        v = K.deref(m.x[2])
        self.assertIsInstance(v, K.Vec)
        self.assertFalse(v.heap)
        self.assertEqual([K.resolve(a) for a in v.args][0::2], [A('x'), 7])
        # the elements are the list's own terms (INFERENCE, KP_UPTACC
        # set_old_value_info binds through the vector)
        self.assertIs(v.args[1], e)
        self.assertEqual(K.deref(m.x[0]), A('t'))
        m.op_stack_vector(fake, 0, 2, 3, 0, 0)
        self.assertEqual(m.x[3], 3)
        # Tail of a proper list is []; an unbound L refuses
        m.x[0] = lst(1, 2)
        m.op_list_to_vector(fake, 0, 0, 0, 1, 0)
        self.assertEqual((len(K.deref(m.x[0]).args), K.deref(m.x[1])), (2, K.NIL))
        m.x[0] = K.Var()
        with self.assertRaises(K.Refusal):
            m.op_list_to_vector(fake, 0, 0, 0, 1, 0)

    def test_heap_vector(self):
        # blt 05 heap_vector(V, ^N) (step 3i): KPEXTENT.ESP:109-120, on the
        # cells of check_last/1 @1d4 `05 00 00 00` and get_address/3 @19c
        # `05 01 02 00`; a heap vector answers its length, a stack vector,
        # an atom or an unbound variable fails (as blt 06 the reverse)
        m = kappa_machine()
        code = m.code('kappa##kappaFLM_extent_manager')
        hv = K.Vec([A('x'), A('end_of_extent')], heap=True)

        def at(off, reg, x):
            w = code.cells[off][3]
            m.reset()
            m.x[reg] = x
            m.handlers[('blt', '05')](code, off, (w >> 16) & 255, (w >> 8) & 255, w & 255, w)
            return m.pc
        self.assertEqual(at(0x1d4, 0, hv), (code, 0x1d5))
        self.assertEqual(m.x[0], 2)
        self.assertEqual(at(0x19c, 1, hv), (code, 0x19d))
        self.assertEqual(m.x[2], 2)
        for x in (K.Vec([A('x')]), A('a'), K.Var()):
            self.assertNotEqual(at(0x19c, 1, x), (code, 0x19d), x)
        with self.assertRaises(K.Refusal):
            m.op_heap_vector(types.SimpleNamespace(id='test', cells={}), 0, 1, 2, 1, 0)

    def test_switch_on_list_nil(self):
        # pmi c9's first target is [] only (step 3i): fts##post_cts local
        # post_cts_list/1 @5b (utter source/FTS/cts_post.esp:18-21
        # `post_cts_list([]):- !; post_cts_list([Tree|TRest]):- ...`) sends
        # [] to @66 `d2`, past the clause's get_nil @65.  A non-nil atom or
        # an integer must fail, as the source does
        lib = K.LB.Librarian()
        lib.load_held(pkgs=['fts'])
        m = K.Machine(lib)
        cid = 'fts##post_cts'
        (p,) = [p for p in lib.templates[cid].locals if (p.name, p.offset) == ('post_cts_list', 0x5b)]

        def n(x):
            m.reset()
            return sum(1 for _ in m.solve((m.code(cid), p.offset), [x]))
        self.assertEqual([n(x) for x in (K.NIL, A('foo'), 5, K.Str('s'))], [1, 0, 0, 0])
        self.assertEqual(n(K.Var()), 1)    # the try chain, clause 1 ([]) cuts

    def test_other_entries_refused(self):
        # a 6c whose entry is not a c9 or a c6 00 00 00, and a 6c whose
        # targets differ from its entry's (MEASURED: 297 and 183 held uses)
        m = machine()
        for e, w in ((0xc7000000, 0), (0xc9000005, 0x00170015)):
            code = types.SimpleNamespace(id='test', cells={
                0: (0, 0x20, 0, e), 1: (0, 0x00, 0, w),
                4: (0, 0x20, 0, 0x6c000000), 5: (0, 0x00, 0, 0xfffa0012), 6: (0, 0x00, 0, 0x000ffffb)})
            m.reset()
            m.x[0] = K.NIL
            with self.assertRaises(K.Refusal) as r:
                m.op_execute_local_switch(code, 4, 0, 0, 0, 0x6c000000)
            self.assertEqual(r.exception.cause, 'operand')


class Census(unittest.TestCase):
    def test_census(self):
        rows = K.census(K.Machine(K.load_six()))
        self.assertEqual(len(rows), 530)
        self.assertEqual(len({r[0] for r in rows}), 103)
        out = {}
        for r in rows:
            out[r[3]] = out.get(r[3], 0) + 1
        # step 3e's pmi ca: 4 refused methods now succeed (array_index_buffer
        # and wshell_buffer set_all_at/2, reset_all_at/2) and 1 fails
        # (csp_fep_main_program get/4); was 216 / 303 / 11
        # 2026-11-25: blt 19 new_heap_vector with V != N witnessed
        # (FMT_CONV.ESP:13-16): the 7 methods refused there go on; three
        # succeed (booking_table, local_node_manager, remote_cell_table
        # create/2), the others stop later
        # 2026-11-25: string/3 a type test (fails on an unbound argument):
        # csp_default_write write/2 goes on and runs into the step limit
        # step 3g: pmi c3 witnessed: pe_registers register_type/3 succeeds
        # step 3i: pmi c8 witnessed (HLCSESITTK.ESP:408-424): of its 8 rows
        # 6 succeed (csp_user_command create/5 and set_command_name/2 in
        # pimmcsp, set_command_name/2 in mpsicsp, rasm_one_word/3,
        # graphics_item set_item/2 and get_item/2).  Each reaches the c8
        # only with the census's unbound argument, which takes the try
        # chain and the first clause binds it: unbound probing, not progress
        # step 3k: put_integer's immediate sign-extended (INFERENCE):
        # csp_deref_utility deref/4 succeeds (checked alone on a fresh
        # machine; with the census's unbound arguments, unbound probing,
        # not progress) and collect_vars/5 goes on to `no method` get/4
        self.assertEqual(out, {'refused': 199, 'success': 318, 'failure': 12, 'step limit': 1})
        # the one method the register cut (pmi dd/de) decides here: it fails
        # cleanly with unbound arguments (no source held)
        (r,) = [r for r in rows if r[:3] == ('pimmcsp##pseudo_csp_csbreak_address_table',
                                              'instance', 'csp_mm_reg/3')]
        self.assertEqual(r[3], 'failure')
        rank = {}
        for r in rows:
            if r[3] == 'refused':
                k = K.refusal_key(r[4], r[5])
                rank[k] = rank.get(k, 0) + 1
        # the string built-ins (blt 0b, 2b) take two methods further:
        # csp_default_write write/2 to string/3 on an unbound argument,
        # state_pe reflesh/3 to a draw_string/6 sent to an unbound receiver.
        # unbound/1 (blt 10, step 3c) takes the three `blt 10` methods on:
        # two to an unbound argument, one to a method not loaded
        self.assertEqual(rank, {
            # step 3h: blt e1 witnessed: 10 csp_pe_control rows go on to a
            # slot their class lacks ('no slot' 30 -> 40), 4 state_pe rows to
            # blt f4 (4 -> 8)
            # step 3k: put_integer sign-extended: csp_deref_utility's two
            # `ffff` rows leave 'operand' (9 -> 7); deref/4 succeeds,
            # collect_vars/5 goes on to 'no method' get/4 (56 -> 57)
            'no method': 57, 'no slot': 40, 'built-in': 24, 'unbound receiver': 20,
            # step 3d: subtract_immediate with R != A is witnessed, so six
            # methods go further; five stopped at divide_immediate (R != A)
            # and up_down_icon code/4 at an unbound argument.  Step 3e:
            # divide_immediate and add with R != A are witnessed, so the six
            # draw/2 go further: four stop at multiply_immediate (R != A,
            # still unwitnessed), two at a draw_line/8 sent to an unbound
            # window (scroll_bar_icon, up_down_icon)
            # step 3e: the 8 sends to an integer still holding its slot's
            # template constant are named so (the census makes receivers
            # with new/2, not through their creators)
            # 2026-11-25: blt 19 V != N witnessed: 'operand' 14 -> 7; of the
            # 7, three succeed, two stop at an unbound new_heap_vector length
            # ('unbound argument' 21 -> 23), dummy_kl1_value_cell unify/2 at a
            # slot constant (8 -> 9), wshell_buffer create/2 at a float pool
            # constant ('pool' 1)
            # string/3 a type test: 'unbound argument' 23 -> 22
            # step 3g: multiply_constant R != A witnessed (p_hwin.esp:233):
            # the four draw/2 (predicate_top/bottom_icon, scroll_top/
            # bottom_icon) go on to an execute_graphics_command/2 sent to
            # an unbound receiver: 'operand' 7 -> 3, 'unbound receiver'
            # 16 -> 20
            # step 3i: pmi 6c rowed; its 5 rows here (mpsicsp
            # csp_csbreak_address_table, kl1_tag) enter a switch other than
            # c9 / c6 00 00 00 and refuse as 'operand' (3 -> 8)
            # step 3i: pmi c8: mpsicsp csp_user_command create/5 goes on to
            # pmi a6 ('operand' 8 -> 9), graphics_item match/2 to an
            # equal_string on an unbound argument (22 -> 23)
            'receiver a slot constant': 9, 'unbound argument': 23, 'operand': 7, 'pool': 1,
            'missing opcode blt f4': 8, 'missing opcode blt 44': 4,
            'missing opcode pmi 36': 3,
            # step 3g: pmi c3 (retry) witnessed: pe_registers
            # register_type/3 succeeds (its unbound first argument takes
            # the first clause, nifr); refused 207 -> 206
            'missing opcode blt 63': 2, 'missing opcode blt f5': 1})


if __name__ == '__main__':
    unittest.main()
