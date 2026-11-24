#!/usr/bin/env python3
"""Tests of the reconstructed Librarian loader (psi/librarian.py) and its
known-plaintext check (psi/plaintext.py).  OURS.

    python3 -I psi/test_librarian.py          (about 10 s; no extraction needed:
                                               the .ptf and .esp files are read
                                               from the repo's archives in memory)

1. TM-388's worked examples (§3.2 p.39, §3.4 pp.42-43, read on the page
   images, PDF pp.51, 54, 55): the inheritance orders of ex1, ex2, ex3, the
   ex4/ex5/ex6 loop refused, and the combination of :get(X) in class1,
   under both after-demon orders (TM-388 against the thesis p.243).
2. TH App A Fig. A-1 (p.241-242): the method key, and a hash table whose
   synonyms are contiguous and found through the index.
3. TM-388 §3.5: attributes of one name collapse, the first in inheritance
   order winning; components stay distinct.
4. Loaded-class facts, pinned to what was measured on 2026-11-23 over the
   eleven held packages: every trailer and header read, the per-package
   header-kind counts, the class objects built, the "needs no SIMPOS"
   closures, and a few classes by name.
5. Known plaintext: agreement with the ESP source, pinned per program.

Discriminating (2026-11-23; each injected into librarian.py, the observed
failures recorded, the file restored byte for byte):
  - default after_order 'forward': test_tm388_combination_default fails,
    nothing else;
  - linearisation keeps the LAST occurrence: test_tm388_ex2 (ex2, a, a1, c,
    a2, b1) and test_tm388_ex3 (a, a1, ex3, c, a2, b1) fail, nothing else;
  - attribute flag bit read as 0x20 instead of 0x10: only
    test_known_plaintext fails (every slot's attribute/component kind then
    disagrees with the source).
  - (2026-11-24) a hash table counted as its size word + 1 cells (the old
    numbering) in librarian._tokens: only test_cell_numbering fails.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import librarian as L  # noqa: E402

T = L.Template.synthetic


def tm388_lib(order='reverse'):
    """TM-388 p.38-39: a: a1,a2; b: b1,b2; c: a2,b1; ex1: a,b; ex2: a,c; ex3: a,*,c."""
    lib = L.Librarian(after_order=order)
    for n in ('a1', 'a2', 'b1', 'b2'):
        lib.add(T(n))
    lib.add(T('a', ['a1', 'a2']))
    lib.add(T('b', ['b1', 'b2']))
    lib.add(T('c', ['a2', 'b1']))
    lib.add(T('ex1', ['a', 'b']))
    lib.add(T('ex2', ['a', 'c']))
    lib.add(T('ex3', ['a', '*', 'c']))
    return lib


def names(lib, cid):
    return [x.split('##')[1] for x in lib.build('test##' + cid).order]


def get_lib(order):
    """TM-388 p.42: class2 and class3 each with before/primary/after :get(X);
    class1 has nature class2, class3 and its own three."""
    lib = L.Librarian(after_order=order)

    def three(k):
        return [('instance', 'before', 'get', 2, 'b%d' % k), ('instance', 'primary', 'get', 2, 'p%d' % k),
                ('instance', 'after', 'get', 2, 'a%d' % k)]
    lib.add(T('class2', methods=three(2)))
    lib.add(T('class3', methods=three(3)))
    lib.add(T('class1', ['class2', 'class3'], methods=three(1)))
    return lib


class TM388(unittest.TestCase):
    def test_tm388_ex1(self):
        self.assertEqual(names(tm388_lib(), 'ex1'), ['ex1', 'a', 'a1', 'a2', 'b', 'b1', 'b2'])

    def test_tm388_ex2(self):
        self.assertEqual(names(tm388_lib(), 'ex2'), ['ex2', 'a', 'a1', 'a2', 'c', 'b1'])

    def test_tm388_ex3(self):
        self.assertEqual(names(tm388_lib(), 'ex3'), ['a', 'a1', 'a2', 'ex3', 'c', 'b1'])

    def test_tm388_loop(self):
        lib = L.Librarian()
        lib.add(T('ex4', ['ex5']))
        lib.add(T('ex5', ['ex6']))
        lib.add(T('ex6', ['ex4']))
        with self.assertRaises(L.CycleError):
            lib.build('test##ex4')
        built, failed = lib.build_all()
        self.assertEqual((len(built), len(failed)), (0, 3))

    def test_tm388_combination_default(self):
        lib = get_lib('reverse')
        self.assertEqual(lib.after_order, L.Librarian().after_order)
        m = lib.build('test##class1').instance_methods[('get', 2)]
        self.assertEqual(m.text(), ':get/2 :- b1,b2,b3,(p1;p2;p3;fail),a3,a2,a1')

    def test_thesis_combination(self):
        m = get_lib('forward').build('test##class1').instance_methods[('get', 2)]
        self.assertEqual(m.text(), ':get/2 :- b1,b2,b3,(p1;p2;p3;fail),a1,a2,a3')

    def test_tm388_before_demon_class_method(self):
        """TM-388 p.43: ex1 has `before :p(_,Y)`, ex2 (nature ex1) `:p(_,X)`;
        both class methods, so :p of ex2 runs ex1's demon then ex2's primary."""
        lib = L.Librarian()
        lib.add(T('ex1', methods=[('class', 'before', 'p', 2, 'd1')]))
        lib.add(T('ex2', ['ex1'], methods=[('class', 'primary', 'p', 2, 'd2')]))
        co = lib.build('test##ex2')
        self.assertEqual(co.class_methods[('p', 2)].text(), ':p/2 :- d1,(d2;fail)')
        self.assertEqual(co.instance_methods, {})
        self.assertIs(lib.send(co, 'class', 'p', 2), co.class_methods[('p', 2)])
        self.assertIsNone(lib.send(co, 'instance', 'p', 2))


class FigA1(unittest.TestCase):
    def test_method_key(self):
        self.assertEqual(L.method_key(5, 2), 2 * 2 ** 24 + 5 + 2)

    def test_table(self):
        keys = [3, 11, 19, 4, 100, 7, 15, 1 << 24 | 3]     # several share low bits
        h = L.HashTable([(k, 'v%d' % k) for k in keys])
        self.assertEqual(h.bits, 3)
        self.assertEqual(h.mask, 7)
        self.assertEqual(len(h.index), 8)
        self.assertEqual(sum(c for _b, c in h.index), len(keys))
        for k in keys:
            self.assertEqual(h.lookup(k), 'v%d' % k)
        self.assertIsNone(h.lookup(27))
        base, count = h.index[3]
        self.assertEqual(sorted(k for k, _v in h.contents[base:base + count]), [3, 11, 19, 1 << 24 | 3])


class Slots(unittest.TestCase):
    def test_slot_collapse(self):
        S = L.Slot
        lib = L.Librarian()
        lib.add(T('base', instance_slots=[S('x', 0x10, ('const', 1)), S('test##base$c', 0, ('const', 0))]))
        lib.add(T('sub', ['base'], instance_slots=[S('x', 0x10, ('const', 2)),
                                                   S('test##sub$c', 0, ('const', 0))]))
        co = lib.build('test##sub')
        self.assertEqual([(e.name, e.owner, e.slot.init) for e in co.instance_slots],
                         [('x', 'test##sub', ('const', 2)), ('test##sub$c', 'test##sub', ('const', 0)),
                          ('test##base$c', 'test##base', ('const', 0))])
        self.assertEqual(lib.slot_number(co, 'instance', 'test##base$c'), 2)


# measured 2026-11-23: (classes, classes with an unloaded ancestor, nature
# resolution, header kinds of every predicate the trailer names)
PINNED = {
    'pimfep': (47, 35, {'held': 14, 'simpos': 25},
               {'11': 387, '12': 71, '25': 108, '27': 1, '35': 468, '36': 2, '37': 9}),
    'pimscsi': (24, 14, {'held': 10, 'simpos': 16},
                {'11': 98, '12': 94, '25': 45, '27': 2, '32': 11, '35': 145, '36': 2, '37': 1}),
    'pimmcsp': (281, 96, {'held': 283, 'simpos': 106},
                {'11': 1593, '12': 673, '22': 8, '25': 254, '27': 5, '32': 24, '35': 1805, '36': 9, '37': 26}),
    'pimmutil': (51, 38, {'simpos': 55, 'held': 24},
                 {'11': 543, '12': 387, '25': 19, '27': 3, '32': 17, '35': 190, '36': 3, '37': 4}),
    'mpsicsp': (30, 17, {'held': 16, 'simpos': 15},
                {'11': 137, '12': 70, '22': 1, '25': 49, '27': 1, '32': 2, '35': 136, '36': 5, '37': 5}),
    'paragraph': (121, 16, {'held': 61, 'simpos': 52},
                  {'11': 851, '12': 910, '22': 6, '25': 114, '27': 4, '32': 3, '35': 512, '36': 1, '37': 1}),
    'kappa': (797, 176, {'simpos': 419, 'held': 472},
              {'11': 7675, '12': 7447, '22': 18, '25': 530, '26': 1, '27': 8, '32': 306, '35': 5014,
               '36': 78, '37': 119}),
    'fts': (21, 7, {'simpos': 7, 'held': 8}, {'11': 217, '12': 115, '25': 89, '35': 6}),
    'qxt': (19, 1, {'held': 4, 'simpos': 1}, {'11': 302, '12': 63, '25': 122, '27': 1, '35': 1}),
    'sancho2': (18, 0, {'held': 7}, {'11': 147, '12': 9, '25': 60}),
    'tour': (46, 4, {'simpos': 8}, {'11': 447, '12': 85, '25': 183, '27': 2, '32': 28, '35': 13}),
}
SIX = ('pimfep', 'pimscsi', 'pimmcsp', 'pimmutil', 'mpsicsp', 'paragraph')


class Held(unittest.TestCase):
    lib = None

    @classmethod
    def setUpClass(cls):
        if Held.lib is None:
            Held.lib = L.Librarian()
            Held.lib.load_held()

    def test_held_templates(self):
        lib = self.lib
        self.assertEqual(len(lib.templates), 1455)
        bad = {c: t.failures for c, t in lib.templates.items() if t.failures}
        self.assertEqual(bad, {})
        unref = sum(len(t.unreferenced_headers) for t in lib.templates.values())
        self.assertEqual(unref, 0)
        rows = {r['package']: (r['classes'], r['partial'], r['natures'], r['kinds'])
                for r in L.package_report(lib)}
        self.assertEqual(rows, PINNED)
        built, failed = lib.build_all()
        self.assertEqual((len(built), failed), (1455, {}))
        # every nature vector is fully qualified; only one class writes `*`
        self.assertEqual([n for t in lib.templates.values() for n in t.natures if '##' not in n], [])
        self.assertEqual([c for c, t in lib.templates.items() if t.natures[0] != c],
                         ['pimmcsp##csp_write_messages'])

    def test_held_classes(self):
        lib = self.lib
        co = lib.build('paragraph##time_graph_window')
        self.assertFalse(co.complete)
        self.assertEqual([r for r, _s in co.opaque], ['simpos##labeled_sash', 'simpos##as_mouse_input',
                                                       'simpos##as_graphics', 'simpos##inferior_window'])
        # p_tgraph.esp:76 `after:create(_,_,Obj)` and :81-82 the two attributes
        self.assertEqual(co.class_methods[('create', 3)].text(), ':create/3 :- (fail),time_graph_window')
        slots = [(e.name, e.slot.flag, e.slot.init[0]) for e in co.instance_slots]
        self.assertEqual(slots, [('display_pos', 0x12, 'code'), ('icon_font', 0x10, 'const')])
        self.assertEqual(co.instance_slots[0].slot.init[1].kind, 0x32)
        self.assertIs(lib.send(co, 'instance', 'draw', 3), co.instance_methods[('draw', 3)])
        self.assertEqual(lib.slot_number(co, 'instance', 'icon_font'), 1)
        p = co.instance_methods[('draw', 3)].primaries[0][1]
        self.assertEqual((p.offset, p.cells[0][0]), (0x68, 0x68))
        # `*` in the middle (pimmcsp, no source held)
        co = lib.build('pimmcsp##csp_write_messages')
        self.assertTrue(co.complete)
        self.assertEqual(co.order[:4], ['pimmcsp##csp_write_messages_before', 'pimmcsp##csp_halt_messages',
                                        'pimmcsp##csp_write_messages', 'pimmcsp##csp_write_messages_after'])
        # kappa `slot is Class`: flag 0x11 attribute, 0x01 component
        t = lib.templates['kappa##kappaREP_editor']
        s = [x for x in t.instance_slots if x.name == 'tbd'][0]
        self.assertEqual((s.flag, s.init), (0x11, ('is', 'kappa##kappaUTL_table_definition')))
        # the dynamic-predicate field (tour_bel.esp:177-195)
        t = lib.templates['tour##tt_belief_system']
        self.assertEqual(len(t.dynamic), 19)

    def test_cell_numbering(self):
        """psi/README.md "Cell numbering": with tables spanning
        mask+1 + 2*keys + 2 cells, every predicate's first cell is numbered
        its header's offset and every local call (pmi 60/61/62, target
        cell + 2 + signed 16 bits) lands on a predicate's code."""
        n = calls = 0
        for t in self.lib.templates.values():
            offs = {p.offset for p in t.preds() if p is not None}
            for p in t.preds():
                if p is None or not p.cells:
                    continue
                n += 1
                self.assertEqual(p.cells[0][0], p.offset, (t.id, p))
                for c in p.cells:
                    if c[1] == 0x20 and c[3] >> 24 in (0x60, 0x61, 0x62):
                        s16 = c[3] & 0xffff
                        tgt = c[0] + 2 + (s16 - 0x10000 if s16 & 0x8000 else s16)
                        calls += 1
                        self.assertIn(tgt, offs, (t.id, p, c))
        self.assertEqual(n, 32901)
        self.assertEqual(calls, 35542)

    def test_held_free_closures(self):
        lib = self.lib
        six = [c for c in lib.templates if lib.templates[c].package in SIX]
        self.assertEqual(len(six), 554)
        self.assertEqual(len(lib.free_of_simpos(six, 'natures')), 338)
        free = lib.free_of_simpos(six, 'union')
        self.assertEqual(len(free), 104)
        self.assertIn('pimfep##fep_command_code_table', free)
        self.assertIn('pimmcsp##dummy_kl1_value_cell', free)
        self.assertEqual(len(lib.free_of_simpos(None, 'union')), 369)
        self.assertEqual(len(lib.free_of_simpos(None, 'natures')), 1051)


# measured 2026-11-23 (psi/plaintext.py): matched, all-agree, and agree/total
# for nature lists, slots, methods, demons, locals
PLAIN = {
    'paragraph': (109, 107, (109, 109), (607, 608), (557, 558), (5, 5), (712, 712)),
    'kappa2': (739, 734, (739, 739), (2957, 2957), (5539, 5693), (206, 206), (7562, 7570)),
    'utter': (69, 67, (69, 69), (109, 109), (382, 382), (3, 3), (874, 878)),
}


class Plaintext(unittest.TestCase):
    def test_known_plaintext(self):
        import plaintext
        for prog, want in PLAIN.items():
            c = plaintext.run(prog)['counts']
            got = (c['matched_exact'] + c['matched_folded'], c['classes_all_agree'],
                   (c['nature_lists_agree'], c['nature_lists']), (c['slots_agree'], c['slots']),
                   (c['methods_agree'], c['methods']), (c['demons_agree'], c['demons']),
                   (c['locals_agree'], c['locals']))
            self.assertEqual(got, want, prog)
            self.assertEqual(c['cause_unexplained'], 0, prog)


if __name__ == '__main__':
    unittest.main(verbosity=1)
