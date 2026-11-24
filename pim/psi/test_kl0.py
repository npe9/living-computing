#!/usr/bin/env python3
"""Tests of the KL0 interpreter (psi/kl0.py) on the held compiled code.  OURS.

    python3 -I psi/test_kl0.py        (a few seconds; reads the .ptf files and
                                       pimos.tar.Z from the repo's archives in
                                       memory, extracts nothing)

1. The opcode table (psi/kl0_opcodes.tsv) is the dispatch: one handler per
   witnessed row, no handler without a row, every row with a witness.
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
4. The census of the 104 classes that need no SIMPOS (103 with methods):
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
    instead of the barrier in A_A: only test_census fails (success 299,
    failure 10: pimmcsp##pseudo_csp_csbreak_address_table csp_mm_reg/3,
    whose source is not held, succeeds instead of failing).
  (Rerun with the session's injection script after any change to the
  tests; the set above was observed on the final tests.)
"""
import os
import sys
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
        self.assertEqual(len(rows), 91)


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


class Census(unittest.TestCase):
    def test_census(self):
        rows = K.census(K.Machine(K.load_six()))
        self.assertEqual(len(rows), 530)
        self.assertEqual(len({r[0] for r in rows}), 103)
        out = {}
        for r in rows:
            out[r[3]] = out.get(r[3], 0) + 1
        self.assertEqual(out, {'refused': 221, 'success': 298, 'failure': 11})
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
        self.assertEqual(rank, {
            'no method': 55, 'no slot': 30, 'built-in': 24, 'unbound receiver': 13,
            'receiver not an object': 8, 'unbound argument': 17, 'operand': 16,
            'missing opcode blt e1': 14, 'missing opcode pmi c8': 8,
            'missing opcode pmi 6c': 5, 'missing opcode pmi ca': 5,
            'missing opcode blt f4': 4, 'missing opcode blt 44': 4,
            'missing opcode blt 25': 3, 'missing opcode pmi 36': 3,
            'missing opcode blt 10': 3, 'missing opcode pmi 37': 3,
            'missing opcode blt 63': 2, 'missing opcode blt f5': 1,
            'missing opcode blt 0b': 1, 'missing opcode pmi c3': 1,
            'missing opcode blt 2b': 1})


if __name__ == '__main__':
    unittest.main()
