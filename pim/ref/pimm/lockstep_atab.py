#!/usr/bin/env python3
"""Lockstep: the IPL's own atom table (ipl_loader:atom_table/1).

    python3 ref/pimm/lockstep_atab.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_atab.py compare

atom_table/1 is the table the IPL's loader interns names in (object
code, asm/kbndis.py ipl_loader atom_table/1, set_ipl_atoms/3,
atom_table/2, intern/5):

    atom_table(In) :-
        keyed_set(P, 10000),            a pool of 16384 slots
        P = [put("[]", [], _) | P1],    the name of nil
        set_ipl_atoms(["pimos", "pim", "go"], P1, P2),
                                        each: new_atom(A), put(Name, A, _)
        atom_table(In, P2).
    atom_table([intern(Name, Atom) | In], P) :-
        P = [empty(Name, YN) | P1], intern(YN, Name, Atom, P1, P2), ...
    intern(yes, Name, Atom, ..) :- new_atom(A), Atom = A, put(Name, A, _)
    intern(no,  Name, Atom, ..) :- get_and_put(Name, Atom, Atom)
    atom_table([Other | In], P) :- P = [Other | P1], ...   passed on
    atom_table([], P) :- P = [].

(a reading of the object code, not a source: the IPL's KL1 is not
held.)  "pimos", "pim" and "go" name the boot entry pimos::pim:go/4.

Two parts:
  1. the table: 19 intern requests for 11 names (repeats; the name of
     nil; the IPL's three; two pairs made to collide, below), then
     get_all(L) sent through the table's own stream (the "passed on"
     clause), which empties the pool and is the IPL's own readback
     (make_atom_symbol_table/2 uses it), then the stream closed.
     Checked: every intern answer is what the table holds for that
     name; one atom per name and no atom twice; "[]" is nil; the
     IPL's three are there; none is one of the image's 486 atoms; no
     goal is left waiting.
  2. a file loaded: lockstep_load.py's first run, with the intern
     requests of ipl_loader:load_file/9 answered by atom_table/1 and
     not by the test.  The table is read back through the tail of the
     loader's requests and the module object is checked cell by cell
     (lockstep_newm.check_record) with each of the file's atoms being
     the atom THE TABLE gives its name, so the check does not rest on
     how new_atom numbers.  The test stands in only for the file's
     buffers.  Two goals are left waiting, those that would show the
     file's name on the console (FileName is never given; C1).

New on both models:
  new_atom       a counter up from 10000h: the numbering is OURS
  hash           PDSS's function (emulator/blt_system.c), not known to
                 be PIM/m's; where a name lies in the pool is therefore
                 not the machine's
  wait_value     on two strings: equal when the descriptors and every
                 word are (PDSS passive_unify)
  floating_point_not_less_than
                 fails unless both are floats (PDSS manual); the pool
                 tries it on every key that is neither atom nor integer
and the first run of put_reused_structure on a list cell and of
put_structured_constant on a string and a list of strings.

Observed fault injections into the Bluespec, 2026-11-23, each FAILed
in part 1 at the trace line shown and was restored:
  new_atom: the counter not advanced         17052: R 5, the second atom
  new_atom: starts at 20000h                 17016: R 5, the first atom
  hash: the string's last word left out      16874: R 0, the code
  hash: NewX is 0                            16875: R 3
  string equality: always equal              18303: the clause taken
  ... only the first word compared           22299 (abcdef, abxyef)
  ... descriptors not compared               26785 (abc, abc and a zero;
                                             NOT caught before that pair
                                             was added)
  float guard succeeds on a non-float        16812: the next instruction
NOT caught, because not run:
  hash of an atom gives 0                    not run by this test; caught
                                             since by lockstep_run.py (line
                                             633 of its part 2); a list or
                                             vector given to the hash
                                             instruction itself is still
                                             not run
  float guard reads its first register twice needs a float in the second
  a string and an atom: wait_value succeeds  never compared

The same wrong rule in BOTH models, where the trace cannot show it,
tried on the reference model alone:
  strings always equal     reported: 'intern and the table differ',
                           'not in the table', 'names in the table'
  new_atom never advances  reported: 'two names share an atom'
  hash always 7            passes, as it must: any function is correct
A count on the reference model: 22 string comparisons equal, 16
unequal, 64 float guards, in the run before the abc pair was added.

Re-pinned for the merger timing change (2026-11-24, docs/
pimm_semantics.md merge: a woken goal of merge_in goes on the
merger's list, taken before the ready queue), 2058423 -> 2058801
trace lines, both models identical and every check passing (injection line numbers above, if any, are as observed before it).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_deca as deca  # noqa: E402
import lockstep_file as lfile  # noqa: E402
import lockstep_gca as gca  # noqa: E402
import lockstep_load as lload  # noqa: E402
import lockstep_modc as modc  # noqa: E402
import lockstep_newm as newm  # noqa: E402

PINNED = dict(parts=2, lines=2058801, names=11, cells=366)


def jis(text):
    """A name as the object files hold it: two-byte JIS, row 23 the
    letters and digits (asm/psdpim.py)."""
    return [0x2300 | ord(c) for c in text]


# Asked in this order.  abcdef and abxyef are three words each with
# the same first and last word: the same hash code by PDSS's function,
# so the pool must tell them apart by comparing the strings.
# ABC0 is abc and a zero element: the same two words as abc under
# another descriptor (no padding), so the same hash code again.
ABC0 = [0x2361, 0x2362, 0x2363, 0]
ASKED = ['foo', 'bar', 'foo', None, 'pimos', 'abcdef', 'abxyef', 'go', 'bar', 'pim',
         'abcdef', 'q', 'abc', ABC0, 'foo', None, 'abxyef', 'abc', ABC0]
IPL_ATOMS = ['pimos', 'pim', 'go']


def words(name):
    if isinstance(name, list):
        return name
    return deca.NIL_NAME if name is None else jis(name)


def table(s, im, names):
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    s.label('the table')
    s.newvar(0)
    s.arg(1, 0)
    s.spawn(pimm.predicate(im, 'ipl_loader', 'atom_table/1'), 1)
    s.run()
    for name in ASKED:
        # the stream's tail is slot 0; the name in 4, the request in
        # 11..13, the list cell in 9, 10
        s.string(4, 16, words(name))
        s.vector(5, 11, [A('intern'), ('slot', 4), None])
        s.cons(6, 9, ('slot', 5), None)
        s.unify(0, 6)
        s.run()
        s.out(13)
        s.live()
        s.setslot(0, s.live_slot[10])
    readback(s, A)


def readback(s, A):
    """get_all(L) through the table's stream, then the stream closed."""
    s.vector(5, 11, [A('get_all'), None])
    s.cons(6, 9, ('slot', 5), None)
    s.unify(0, 6)
    s.run()
    s.out(12)
    s.live()
    s.setslot(0, s.live_slot[10])
    s.unifyc(0, (pimm.ATOM, 0))
    s.run()


def load(s, im, names, words):
    """lockstep_load.py's first run, the intern requests answered by
    atom_table/1 and not by the test."""
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    s.label('a file loaded')
    # 0 the file, 1 FileName, 2 Modules, 3 their tail, 4 Status,
    # 7 intern requests, 8 their tail, 9 Info, 10 normal(File)
    for i in (0, 1, 2, 3, 4, 7, 8, 9):
        s.newvar(i)
    s.arg(1, 7)
    s.spawn(pimm.predicate(im, 'ipl_loader', 'atom_table/1'), 1)
    s.vector(10, 11, [A('normal'), ('slot', 0)])
    for a, sl in ((1, 10), (2, 1), (4, 2), (5, 3), (6, 7), (7, 8), (8, 9), (9, 4)):
        s.arg(a, sl)
    s.argc(3, newm.PACKAGE)
    s.spawn(pimm.predicate(im, 'ipl_loader', 'load_file/9'), 9)
    feed, fs = list(words), None
    while True:
        s.run()
        m = s.live()
        if fs is None:
            fs = s.live_slot[0]
        progress = False
        while feed:
            w = m.deref(fs)
            if m.unbound(w) or w == (pimm.ATOM, 0):
                break
            req = m.deref((pimm.REF, w[1]))
            assert m.deref((pimm.REF, req[1])) == A('getb'), req
            chunk, feed = feed[:lload.BUFFER], feed[lload.BUFFER:]
            s.string(6, 16, chunk)
            s.vector(5, 13, [A('normal'), ('slot', 6)])
            s.setslot(15, (pimm.REF, req[1] + 1))
            s.unify(15, 5)
            fs = (pimm.REF, w[1] + 1)
            m = s.live()
            progress = True
        if not progress:
            break
    for i in (1, 2, 3, 4, 9):
        s.out(i)
    # the table read back through the tail of the loader's requests
    s.vector(5, 11, [A('get_all'), None])
    s.cons(6, 13, ('slot', 5), None)
    s.unify(8, 6)
    s.run()
    s.out(12)
    s.live()
    s.setslot(0, s.live_slot[14])
    s.unifyc(0, (pimm.ATOM, 0))
    s.run()
    return len(feed)


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    table(s, im, names)
    waiting = s.live().nsusp
    words = lfile.file_words(lload.FILE)
    left = load(s, im, names, words)
    return s, dict(im=im, left=left, waiting=waiting, defs=lload.definitions(words),
                   mods=modc.modules(lload.FILE),
                   tops=[a[3] for a in gca.areas(lload.FILE)])


def pairs(m, w):
    """The {Name, Atom} pairs of a get_all answer: {name words: cell}."""
    out, w = {}, m.deref(w)
    while w[0] & ~1 == pimm.LIST:
        e = m.deref(m.mem[w[1]])
        assert m.vsize(e) == 2, e
        b = m.vbase(e)
        bits, elems = m.string(m.deref(m.mem[b]))
        assert bits == 16 and tuple(elems) not in out
        v = m.deref(m.mem[b + 1])
        out[tuple(elems)] = (v[0] & ~1, v[1])
        w = m.deref(m.mem[w[1] + 1])
    assert w == (pimm.ATOM, 0), w
    return out


def check_table(m, im, answers, got):
    """What is wrong with a table read back as `got`, whose intern
    answers were `answers` [(name words, cell)]."""
    bad = []
    NIL = tuple(deca.NIL_NAME)
    for name, w in answers:
        w = m.deref(w)
        if (w[0] & ~1, w[1]) != got.get(tuple(name)):
            bad.append(('intern and the table differ', name, w))
    for name in [NIL] + [tuple(jis(n)) for n in IPL_ATOMS]:
        if name not in got:
            bad.append(('not in the table', name))
    if got.get(NIL) != (pimm.ATOM, 0):
        bad.append(('[] is not nil', got.get(NIL)))
    vals = list(got.values())
    if any(t != pimm.ATOM for t, _v in vals):
        bad.append(('not an atom',))
    if len(set(vals)) != len(vals):
        bad.append(('two names share an atom',))
    if any(v in im.sym for name, (_t, v) in got.items() if name != NIL):
        bad.append(("one of the image's own atoms given",))
    return bad


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    ws = got['the table']
    tab = pairs(m, ws[-1])
    bad = check_table(m, want['im'], [(words(n), w) for n, w in zip(ASKED, ws)], tab)
    if set(tab) != {tuple(words(n)) for n in ASKED + IPL_ATOMS}:
        bad.append(('names in the table', len(tab)))
    bad2, cells = check_load(m, want, got['a file loaded'])
    # after the table nothing waits; after the load, the two goals
    # that would show the file's name on the console (ipl:convert/2,
    # display_console_0/1): FileName is never given (C1)
    if want['waiting'] or m.nsusp != 2:
        bad.append(('goals left waiting', want['waiting'], m.nsusp))
    return bad + bad2, len(tab), cells


def check_load(m, want, ws):
    """The module object, its atoms as the IPL's own table gives them."""
    name, out, tail, status, info, back = ws
    if want['left']:
        return [('words not asked for', want['left'])], 0
    if m.unbound(status) or m.term(status) != 'normal':
        return [('status',)], 0
    tab = pairs(m, back)
    bad = check_table(m, want['im'], [], tab)
    words = {k: tuple(n) for k, n in want['defs']}
    if set(tab) != set(words.values()) | {tuple(jis(n)) for n in IPL_ATOMS} \
            | {tuple(deca.NIL_NAME)}:
        bad.append(("the table is not the file's names and the IPL's", len(tab)))
    number = deca.number
    # the file's atom k is the atom the table gives its name
    deca.number = lambda k, name: (tab.get(words[k], (0, -1))[1] if k in words
                                   else number(k, name))
    cells = 0
    try:
        lst = m.deref(out)
        for mod, top in zip(want['mods'], want['tops']):
            if lst[0] & ~1 != pimm.LIST:
                bad.append(('modules list short',))
                break
            b, n = newm.check_record(m, mod, top, m.deref(m.mem[lst[1]]))
            cells += n
            bad += [(mod['name'], x) for x in b]
            lst = m.deref(m.mem[lst[1] + 1])
        if not (m.unbound(lst) and lst[1] == m.deref(tail)[1]):
            bad.append(('the list does not end in ModulesTail',))
    finally:
        deca.number = number
    return bad, cells


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        m = s.live()
        n = len(ASKED) + 1
        s.outs = [('the table' if i < n else 'a file loaded', w)
                  for i, (_l, w) in enumerate(s._live[3])]
        print(check(s, m, want), m.hp - m.load)
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep atab',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, n, cells = check(s, m, want)
    if bad or n != PINNED['names'] or cells != PINNED['cells']:
        print('pimm lockstep atab: FAIL %d names, %r' % (n, bad[:3]))
        return 1
    print("pimm lockstep atab: PASS (the IPL's own atom table, ipl_loader:atom_table/1, on "
          'the Bluespec core, %d trace lines identical to the reference model: %d names, '
          'one atom each, [] nil, read back with get_all; a real object file loaded '
          'against it, its module object of %d cells holding the atoms the table gives)'
          % (s.counts['lines'], n, cells))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
