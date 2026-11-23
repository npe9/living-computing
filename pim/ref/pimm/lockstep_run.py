#!/usr/bin/env python3
"""Lockstep: a predicate of a module the IPL loaded is run (rung R2).

    python3 ref/pimm/lockstep_run.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_run.py compare

The roadmap's R2: "One predicate from a real PIMOS module, loaded
from its .sav, runs to completion with arguments we construct and
returns the right answer."

  1. pimm_patch_hash360E.sav is loaded as in lockstep_atab.py:
     ipl_loader:load_file/9 with the IPL's own reader, checksum and
     atom table.  Its one module is hasher (source: pimos
     src/utility/pool/hash.kl1).
  2. hasher:hash/3 is RUN: a goal is started at the predicate's
     place in the module object (the object's address + the place the
     file gives, which lockstep_newm.check_record checks against the
     object's own entry table), so every instruction is fetched from
     the heap, from cells the IPL wrote.  Ten inputs: six integers,
     an atom, a string, a list, a vector of five.  After each, the
     same input is given to the image's own ipl_pool:hash/3, the same
     code compiled into the IPL.

Checked, per input: H is what the KL1 source gives (by_source below,
a transcription); NewX is X as a term; the image's twin gives the
same; no goal is left waiting by the runs; instructions were taken
inside the module object (428 on the reference model).

What the test does that the IPL would: it starts the goal.  The
IPL's linker (ipl_link_table) and a call from one loaded module into
another are not run; hasher's other predicate, usage/1, calls
pool_usage, which is not loaded.

The reference model fetched code from the image only; it now reads a
code address past the image and stubs from the heap.  The Bluespec
always fetched from the one memory and needed no change.

New on both models: the guards floating_point (type test), divide and
shift_left, put_marked_variable, read_variable_without_deref (see
docs/pimm_semantics.md for each one's source).

Observed fault injections into the Bluespec, 2026-11-23, each FAILed
in part 2 at the trace line shown and was restored:
  floating_point succeeds on a non-float       724: the next clause
  shift_left shifts right                      2434: R 7
  put_marked_variable: references unmarked     881: R 12
  read_variable_without_deref does not advance 841: R 6
  divide gives the remainder                   2216: R 8 (NOT caught
                                               while the vector had
                                               three elements: 3 / 2
                                               is 1 remainder 1)
NOT caught, because not run: divide's overflow refusal.

The same wrong rule in BOTH models, tried on the reference model
alone, is reported by the source's answer: shift_left one too far and
divide one too many (the vector's H), read_variable_without_deref
not advancing (the list's H, NewX and the twin).

Not run: a negative or zero divisor, a float, a module or code
argument, depth beyond one level of structure.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_atab as atab  # noqa: E402
import lockstep_file as lfile  # noqa: E402
import lockstep_load as lload  # noqa: E402
import lockstep_modc as modc  # noqa: E402

PINNED = dict(parts=2, lines=1112850, answers=10)
MIN = 0x80000000


def by_source(x, names):
    r"""H for the input, by the module's KL1 source (pimos
    src/utility/pool/hash.kl1), transcribed:

        hash(X,H,Y) :- true | hash0(X,H,Y,6).
        hash0(X,H,Y,_) :- X>=0 | X=Y,X=H.
        hash0(X,H,Y,_) :- 16#"80000000"<X,X<0 | X=Y,H:= -X.
        hash0(X,H,Y,_) :- X=16#"80000000" | X=Y,H=0.
        hash0(X,H,Y,_) :- atom(X) | builtin:hash(X,H,Y).
        hash0(X,H,Y,_) :- string(X,_,_) | builtin:hash(X,H,Y).
        hash0(X,H,Y,C) :- list(X) | hash_list(X,H,Y,C).
        hash0(X,H,Y,C) :- vector(X,L) | hash_vect(X,H,Y,C,L).
        hash_list([A|X],H,Y,C) :- C>0 | ... hash0(A,M,A1,C1), hash0(X,N,X1,C1),
            H:=(M/\16#"1fffffff")+((N<<2)/\16#"1fffffff")+(N/\16#"1fffffff").
        hash_list(X,H,Y,0) :- true | H:=0,X=Y.
        hash_vect(X,H,Y,Cnt,L) :- Cnt>0,L>0,MP:=L/2,LP:=L-1 |
            elements 0, MP, LP hashed with Cnt-1 to Hf, Hm0, Hl0,
            wait_hashed_value(Hf,Hm0,Hl0,H,L).
        wait_hashed_value: X=16#"3fffffff",
            Hm:=((Hm0<<1)/\X) + (Hm0/\X), Hl:=((Hl0<<2)/\X) + (Hl0/\X),
            H0:=((Hf/\X) + (Hm/\X))/\X, H1:=((Hl/\X) + (L/\X))/\X | H:=H0+H1.

    builtin:hash is the hash instruction, whose function is PDSS's
    here: an atom's number, a string's word count and end words."""
    def h0(x, c):
        if x[0] == 'string':
            n = x[1]
            a, b = n[0] << 16 | n[1], n[2] << 16        # three 16-bit elements
            return pimm.signed((2 + a + (a >> 16) + (a >> 24) + (b << 1) + (b >> 15)
                                + (b >> 23)) & 0xffffffff)
        if x[0] == 'list':
            if c == 0:
                return 0
            m = h0(x[1][0], c - 1)
            n = h0(('list', x[1][1:]) if x[1][1:] else (pimm.ATOM, 0), c - 1)
            k = 0x1fffffff
            return (m & k) + ((n << 2) & k) + (n & k)
        if x[0] == 'vector':
            ln = len(x[1])
            if c == 0 or ln == 0:
                return 0
            hf, hm0, hl0 = [h0(x[1][i], c - 1) for i in (0, ln // 2, ln - 1)]
            k = 0x3fffffff
            hm = ((hm0 << 1) & k) + (hm0 & k)
            hl = ((hl0 << 2) & k) + (hl0 & k)
            return (((hf & k) + (hm & k)) & k) + (((hl & k) + (ln & k)) & k)
        if x[0] == pimm.ATOM:
            return x[1]
        v = pimm.signed(x[1])
        return 0 if v == -1 << 31 else abs(v)
    return h0(x, 6)


def inputs(names):
    """(what, the input, H by the source)."""
    I = lambda v: (pimm.INT, v & 0xffffffff)       # noqa: E731
    ins = [
        ('5', I(5)),
        ('0', I(0)),
        ('-7', I(-7)),
        ('the least integer', I(MIN)),
        ('the greatest integer', I(0x7fffffff)),
        ('-1', I(-1)),
        ('an atom', (pimm.ATOM, names['normal'])),
        ('a string', ('string', atab.jis('abc'))),
        ('a list', ('list', [I(3), I(4)])),
        # five elements: the middle is 5 / 2, quotient 2, remainder 1
        ('a vector', ('vector', [I(3), I(-4), I(5), I(6), I(-9)])),
    ]
    return [(what, x, by_source(x, names)) for what, x in ins]


def put(s, x):
    """slot 0 := the input."""
    if x[0] == 'string':
        s.string(0, 16, x[1])
    elif x[0] == 'list':
        s.cons(4, 5, x[1][1], (pimm.ATOM, 0))
        s.cons(0, 7, x[1][0], ('slot', 4))
    elif x[0] == 'vector':
        s.vector(0, 5, x[1])
    else:
        s.setslot(0, x)


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    words = lfile.file_words(lload.FILE)
    left = atab.load(s, im, names, words)
    m = s.live()
    # the module object: the record's fourth element, {MOD, a}
    out = s._live[3][-5][1]
    rec = m.deref(m.mem[m.deref(out)[1]])
    mod = m.deref(m.mem[m.vbase(rec) + 3])
    assert mod[0] == pimm.MOD, mod
    info = modc.modules(lload.FILE)[0]
    loc = dict((n, (a, p)) for n, a, p in info['preds'])['hash']
    assert loc[0] == 3
    loaded = mod[1] + loc[1] - m.load
    twin = pimm.predicate(im, 'ipl_pool', 'hash/3')
    ins = inputs(names)
    s.label('run')
    for _what, x, _h in ins:
        for pc in (loaded, twin):
            put(s, x)
            s.newvar(1)
            s.newvar(2)
            s.arg(1, 0)
            s.arg(2, 1)
            s.arg(3, 2)
            s.spawn(pc, 3)
            s.run()
            s.out(1)
            s.out(2)
            s.out(0)
    return s, dict(left=left, ins=ins, loaded=loaded, waiting=s.live().nsusp,
                   span=(mod[1] - m.load, mod[1] - m.load + info_len(m, mod)))


def info_len(m, mod):
    return (m.mem[mod[1]][1] & 0xffffff) + 1


def check(s, m, want, lines):
    bad, n = [], 0
    outs = [w for label, w in s.outs if label == 'run']
    if want['left']:
        bad.append(('words not asked for', want['left']))
    if len(outs) != 6 * len(want['ins']):
        return [('answers', len(outs))], 0
    for k, (what, _x, by_hand) in enumerate(want['ins']):
        h1, x1, x, h2, x2, xt = [m.deref(w) for w in outs[6 * k:6 * k + 6]]
        if m.unbound(h1) or m.unbound(x1):
            bad.append((what, 'no answer from the loaded code'))
            continue
        n += 1
        if h1[0] & ~1 != pimm.INT or pimm.signed(h1[1]) != by_hand:
            bad.append((what, 'H', h1, by_hand))
        # NewX is X as a term: a list or vector comes back rebuilt
        # (put_reused_structure makes new cells here)
        if m.term(x1) != m.term(x):
            bad.append((what, 'NewX is not X', m.term(x1), m.term(x)))
        if m.unbound(h2) or (h1[0] & ~1, h1[1]) != (h2[0] & ~1, h2[1]) \
                or m.term(x2) != m.term(xt):
            bad.append((what, "the image's twin differs", h1, h2))
    # instructions taken inside the module object
    lo, hi = want['span']
    ran = sum(1 for ln in lines if ln[0] == 'I' and lo <= int(ln.split()[1]) < hi)
    if not ran:
        bad.append(('no instruction of the loaded module was taken',))
    # two goals wait from the load (the file's name on the console),
    # none from the runs
    if want['waiting'] != 2 or m.nsusp != 2:
        bad.append(('goals waiting', want['waiting'], m.nsusp))
    return bad, n, ran


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        lines = [x for _w, ls in s.play() for x in ls]
        print(check(s, s.machine, want, lines), len(lines))
        return 0
    s.all_lines = []
    play = s.play

    def keeping():
        for what, lines in play():
            s.all_lines += lines
            yield what, lines
    s.play = keeping
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep run',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, n, ran = check(s, m, want, s.all_lines)
    if bad or n != PINNED['answers']:
        print('pimm lockstep run: FAIL %d answers, %r' % (n, bad[:3]))
        return 1
    print("pimm lockstep run: PASS (hasher:hash/3, loaded from a real object file by the "
          "IPL's own loader and atom table, RUN from the module object on the Bluespec "
          'core: %d trace lines identical to the reference model, %d instructions taken '
          "in the heap; %d answers, each what the module's KL1 source gives and equal "
          "to the image's ipl_pool:hash/3)" % (s.counts['lines'], ran, n))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
