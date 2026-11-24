#!/usr/bin/env python3
"""Tests of the KL0 interpreter (psi/kl0.py) on the held compiled code.  OURS.

    python3 -I psi/test_kl0.py        (a few seconds; reads the .ptf files and
                                       pimos.tar.Z from the repo's archives in
                                       memory, extracts nothing)

1. The opcode table (psi/kl0_opcodes.tsv) is the dispatch: one handler per
   witnessed row, no handler without a row, every row with a witness.
   The four string rows (blt 0b, 1c, 23, 2b) run on their witness
   operands, new_string with S != T included (view_select_menu change/3).
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
            self.assertEqual(r['status'], 'KNOWN-PLAINTEXT', r)
        m = machine()
        self.assertEqual(set(m.handlers), set(keys))
        ops = {n[3:] for n in dir(K.Machine) if n.startswith('op_')}
        self.assertEqual(ops, {r['mnemonic'] for r in rows})
        # 100 before step 3c's nine rows (blt 01 06 10 16 32 33 40 5c 68),
        # 109 before step 3d's four (blt 6e 34, pmi b0 b4), 113 before
        # step 3e's pmi ca
        self.assertEqual(len(rows), 114)

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
        m.op_add_immediate(None, 0, 0, 1, 6, None)
        m.op_subtract_immediate(None, 0, 4, 11, 0, None)
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
        with self.assertRaises(K.Refusal):
            m.op_add(None, 0, 1, 0, 2, None)    # R != A: unwitnessed
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
        lib = K.LB.Librarian()
        lib.load_held(pkgs=['kappa'])
        cls.m = K.Machine(lib)

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
        self.assertEqual(out, {'refused': 211, 'success': 307, 'failure': 12})
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
            'no method': 56, 'no slot': 30, 'built-in': 24, 'unbound receiver': 14,
            # step 3d: subtract_immediate with R != A is witnessed, so six
            # methods go further; five stop at divide_immediate (R != A, still
            # unwitnessed) and up_down_icon code/4 at an unbound argument
            'receiver not an object': 8, 'unbound argument': 21, 'operand': 16,
            'missing opcode blt e1': 14, 'missing opcode pmi c8': 8,
            'missing opcode pmi 6c': 5,
            'missing opcode blt f4': 4, 'missing opcode blt 44': 4,
            'missing opcode pmi 36': 3,
            'missing opcode blt 63': 2, 'missing opcode blt f5': 1,
            'missing opcode pmi c3': 1})


if __name__ == '__main__':
    unittest.main()
