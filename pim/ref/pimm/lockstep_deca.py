#!/usr/bin/env python3
"""Lockstep: the IPL's file decoder on atoms, proper lists, and real .sav terms.

    python3 ref/pimm/lockstep_deca.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_deca.py compare

lockstep_dect.py, with the decoder's other two conversations (read
from the object code; asm/kl1decomp.py get_atom_name/6):

  with the reader, besides [W|Rest] and {V, Rest}:
    {Buf, Out, Rest}    Buf is a new string; as many 16-bit words as it
                        has elements are wanted, as a string, in Out

  with the atom table, on the AT stream:
    [put(Id, Name, Atom)|AT]    a new atom: Name is its name (a 16-bit
                                string), the atom is wanted in Atom
    [get(Id, Atom)|AT]          the atom already given for Id

An atom in the file is 0000, then a word Id: 8000 + n defines atom n
and is followed by its length (32 bits) and its characters, a word
each; below 8000 it refers to atom n (encoder.kl1, asm/unlsav.py).

This test plays the reader and the atom table.  Atoms are numbered by
it: [] (the name is the two JIS brackets 214E 214F; unlsav.py shows
their low bytes, "NO") is the atom 0, any other atom n is 10000h + n.
For a put, the Name the decoder hands over is checked against the
words of the file: that is the check on the string path.

Terms: some written here, and the first terms of the GC areas of the
real pimm_kernel360E.sav that consist of integers, atoms, lists,
vectors of at most 40 elements and strings of 8- or 16-bit elements,
at most 40 of them.  For the real ones the words are the file's and the atoms defined earlier in the file are answered as gets.  The oracle
is asm/unlsav.py's reading of the same words.

A string in the file is 06ss (ss the element size), its length (32
bits), then the elements packed from the top into 32-bit words.  The
decoder asks for a 16-bit string whole with {Buf, Out, Rest} (and one
more word when the length is odd), and for an 8-bit one a 32-bit word
at a time, which it unpacks with shifts and set_string_element.

A vector is made with new_vector and filled with set_vector_element;
one of 7 or more elements is the long form with a descriptor (see
pimm.Machine.vsize), which this test is the first to make.

New here: put_constant, and the guard modulo with the Bluespec divide
box (PimmMBox.bsv).

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  put_constant steps one cell        term 0: the constant fetched as an instruction
  put_constant takes 16 bits         term 0: R 6 = ffff8000 for 8000
  put_constant writes r[y]           term 0: R 0 written for R 6

  modulo gives the quotient          the 16-bit string of 2: R 6 = 1 for 0
  divide box one step short          the same: R 6 = 1 for 0
  divide box never subtracts         the same: R 6 = 2 for 0
  b_shift_right arithmetic           the 8-bit string with a5 last: R 3 = ffffffa5
                                     for a5 (in the trace; the element is masked)
  long vector: elements at a+2       the vector of 7: the descriptor's pointer
  long vector: a 6-vector's tag      the same: R 0 = 1d... for 1f...
  long vector: copy reads from the   the same: an element copied as the
    descriptor, not the elements     length 7
  long vector: 3 cells too few       the same: the next allocation overlaps

Not caught: a long vector's size read from the second length cell (the
two are always equal); the vector box without its range check (the
decoder stays in range); the box's info answer, which only the guards
vector and switch_on_non_vector use on a long vector, and no test runs
them on one.
Not caught: modulo accepting a zero divisor, and nothing here divides a
negative number: the decoder only takes a length mod 2.
Not caught: put_constant forcing the integer tag.  Both constants the
decoder loads this way are integers (32768).
"""
import io
import os
import struct
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import unlsav  # noqa: E402

PINNED = dict(parts=32, lines=49485, real=17)
OBJ = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'pimosobj.tar.Z')
NIL_NAME = [0x214e, 0x214f]
REAL = 10            # real terms without strings
REAL_STRINGS = 6     # and with
REAL_LONG = 6        # and with a vector of 7 or more elements


def jis(text):
    return [0x2300 | ord(c) for c in text]


# written terms: an integer; ('a', n, name words or None for a reference);
# ('v', [terms]); ('l', [cars], cdr); ('s', element bits, [elements])
NIL0 = ('a', 1, NIL_NAME)
NIL = ('a', 1, None)
WRITTEN = [
    ('a', 5, jis('abc')),
    ('l', [1, 2], NIL0),
    ('v', [('a', 7, jis('x')), ('a', 7, None), ('a', 8, jis('yz'))]),
    ('l', [('a', 2, jis('p')), ('l', [3], NIL0), ('v', [('a', 2, None)])], NIL),
    ('l', [], NIL0),
    ('s', 16, [0x2341, 0x2342]),
    ('s', 16, [0x2341, 0xffff, 0x8000]),
    ('s', 8, [1, 2, 3, 4]),
    ('s', 8, [0xff, 0x80, 0x7f, 0, 0xa5]),
    ('s', 16, []),
    ('s', 8, []),
    ('v', [('s', 8, [65]), ('l', [('s', 16, [7])], NIL0)]),
    ('v', [1, 2, 3, 4, 5, 6, 7]),
    ('v', [('a', 3, jis('q')), ('v', list(range(9))), 0, ('s', 8, [9]), 4, 5, 6, ('a', 3, None)]),
    ('v', list(range(6))),
]


def encode(t):
    if isinstance(t, int):
        if 0 <= t < 0xff:
            return [0x0100 | t]
        if -256 < t < 0:
            return [0x0200 | t & 0xff]
        return [0x0300, t >> 16 & 0xffff, t & 0xffff]
    if t[0] == 'a':
        if t[2] is None:
            return [0, t[1]]
        return [0, 0x8000 | t[1], len(t[2]) >> 16, len(t[2]) & 0xffff] + t[2]
    if t[0] == 's':
        size, elems = t[1], t[2]
        per = 32 // size
        out = [0x0600 | size, len(elems) >> 16, len(elems) & 0xffff]
        for k in range(0, len(elems), per):
            x = 0
            for j, e in enumerate(elems[k:k + per]):
                x |= e << (32 - size * (j + 1))
            out += [x >> 16, x & 0xffff]
        return out
    if t[0] == 'v':
        n = len(t[1])
        return [0x0700, n >> 16, n & 0xffff] + [w for e in t[1] for w in encode(e)]
    n = len(t[1]) + 1
    return ([0x0800, n >> 16, n & 0xffff] + [w for e in t[1] for w in encode(e)]
            + encode(t[2]))


def number(n, name):
    return 0 if name == 'NO' else 0x10000 + n


def shown(p):
    """asm/unlsav.py's reading as pimm.Machine.term shows the answer."""
    if p[0] == 'int':
        return p[1] - (1 << 32) if p[1] >= 1 << 31 else p[1]
    if p[0] == 'atom':
        n = number(p[1], p[2])
        return [] if n == 0 else '#%x' % n
    if p[0] == 'vector':
        return tuple(shown(e) for e in p[1])
    if p[0] == 'string':
        return (p[2], p[3])
    assert p[0] == 'list', p
    out = shown(p[1][-1])
    for e in reversed(p[1][:-1]):
        out = [shown(e)] + out if isinstance(out, list) else ('|', shown(e), out)
    return out


def has_string(p):
    return p[0] == 'string' or (p[0] in ('vector', 'list') and any(has_string(e) for e in p[1]))


def has_long(p):
    return (p[0] == 'vector' and len(p[1]) > 6) or \
        (p[0] in ('vector', 'list') and any(has_long(e) for e in p[1]))


def simple(p):
    if p[0] in ('int', 'atom'):
        return True
    if p[0] == 'string':
        return p[2] in (8, 16) and p[1] <= 40
    if p[0] == 'vector':
        return 1 <= len(p[1]) <= 40 and all(simple(e) for e in p[1])
    return p[0] == 'list' and all(simple(e) for e in p[1])


def real_terms():
    """(words, atoms known before, unlsav's reading) for the first REAL
    simple terms of the kernel file's GC areas."""
    raw = subprocess.run(['gzip', '-dc', OBJ], stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('pimm_kernel360E.sav'):
                data = tf.extractfile(m).read()
    words = list(struct.unpack('>%dH' % (len(data) // 2), data))
    r = unlsav.Reader(words)
    magic, nmod, _sep = r.rd(), r.rd(), r.rd()
    if magic in (0x5702, 0x5802):
        r.i += 2 + ((words[r.i] << 16) | words[r.i + 1])
    # every term unlsav.parse_module reads at top level (the module
    # information and the GC area), with where it lies in the file
    out, depth, inner, count = [], [0], unlsav.parse_term, [0, 0, 0]

    def outer(rd):
        i, before = rd.i, dict(rd.atoms)
        depth[0] += 1
        try:
            p = inner(rd)
        finally:
            depth[0] -= 1
        if depth[0] == 0 and simple(p) and p[0] != 'int':
            k = 2 if has_long(p) else 1 if has_string(p) else 0
            if count[k] < (REAL, REAL_STRINGS, REAL_LONG)[k]:
                count[k] += 1
                out.append((words[i:rd.i], before, p))
        return p
    unlsav.parse_term = outer
    try:
        for _ in range(nmod):
            unlsav.parse_module(r)
    finally:
        unlsav.parse_term = inner
    return out


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    pc = pimm.predicate(im, 'ipl_file_decoder', 'decode_0/7')
    names = {name: n for n, name in im.sym.items()}
    cases = []
    for t in WRITTEN:
        words = encode(t)
        r = unlsav.Reader(list(words))
        p = unlsav.parse_term(r)
        assert r.i == len(words), t
        cases.append(('written %r' % (t,), words, {}, p))
    real = real_terms()
    for words, before, p in real:
        cases.append(('real %r' % (p,), words, before, p))
    want = []
    for n, (label, words, before, p) in enumerate(cases):
        label = 'term %d: %s' % (n, label[:150])
        # slots: 0 the input, 1 UNLFS, 2 Object, 3 AT, 4 Status, 5 a
        # request's cell, 6 a string for the reader's answer, 7 the atom
        # stream
        s.label(label)
        for i in (0, 1, 2, 3, 4, 7):
            s.newvar(i)
        s.argc(1, (pimm.INT, words[0]))
        s.arg(2, 0)
        s.arg(3, 1)
        s.arg(4, 2)
        s.arg(5, 7)
        s.arg(6, 3)
        s.arg(7, 4)
        s.spawn(pc, 7)
        feed = words[1:]
        m = s.live()
        at, atq = s.live_slot[0], s.live_slot[7]
        table = {k: number(k, v) for k, v in before.items()}
        while True:
            s.run()
            m = s.live()
            progress = False
            while True:                     # the reader
                w = m.deref(at)
                if m.unbound(w):
                    break
                if w[0] & ~1 == pimm.LIST:
                    s.setslot(5, (pimm.REF, w[1]))
                    s.unifyc(5, (pimm.INT, feed[0]))
                    feed, at = feed[1:], (pimm.REF, w[1] + 1)
                elif w[0] & ~1 == pimm.VECT0 + 4:
                    s.setslot(5, (pimm.REF, w[1]))
                    s.unifyc(5, (pimm.INT, feed[0] << 16 | feed[1]))
                    feed, at = feed[2:], (pimm.REF, w[1] + 1)
                elif w[0] & ~1 == pimm.VECT0 + 6:
                    buf = m.deref((pimm.REF, w[1]))
                    if m.unbound(buf):
                        break               # the buffer is not made yet
                    bits, elems = m.string(buf)
                    assert bits == 16
                    k = len(elems)
                    s.string(6, 16, feed[:k])
                    s.setslot(5, (pimm.REF, w[1] + 1))
                    s.unify(5, 6)
                    feed, at = feed[k:], (pimm.REF, w[1] + 2)
                else:
                    raise AssertionError('an unknown request %r' % (w,))
                m = s.live()
                progress = True
            while True:                     # the atom table
                w = m.deref(atq)
                if m.unbound(w):
                    break
                assert w[0] & ~1 == pimm.LIST, w
                req = m.deref((pimm.REF, w[1]))
                size = (req[0] & ~1) - pimm.VECT0 >> 1
                what = m.deref((pimm.REF, req[1]))
                ident = pimm.signed(m.deref((pimm.REF, req[1] + 1))[1])
                if size == 3 and what == (pimm.ATOM, names['get']):
                    answer = table[ident]
                elif size == 4 and what == (pimm.ATOM, names['put']):
                    name = m.deref((pimm.REF, req[1] + 2))
                    if m.unbound(name):
                        break               # the name is not read yet
                    bits, elems = m.string(name)
                    assert bits == 16
                    answer = 0 if elems == NIL_NAME else 0x10000 + ident
                    table[ident] = answer
                    want.append((label, 'name', ident, elems))
                else:
                    raise AssertionError('an unknown atom request %r' % (req,))
                s.setslot(5, (pimm.REF, req[1] + size - 1))
                s.unifyc(5, (pimm.ATOM, answer))
                atq = (pimm.REF, w[1] + 1)
                m = s.live()
                progress = True
            if not progress:
                break
        assert not feed, (label, feed)
        s.setslot(5, at)
        s.setslot(6, atq)
        for i in (1, 2, 3, 4, 5, 6):
            s.out(i)
        want.append((label, 'term', words, p))
    s.real = len(real)
    return s, want


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad = []
    for label, kind, a, b in want:
        if kind == 'name':
            # the name handed to the atom table is the file's words
            words = [w for l2, k2, w, _p in want if l2 == label and k2 == 'term'][0]
            i = [j for j in range(len(words) - 3)
                 if words[j] == 0 and words[j + 1] == 0x8000 | a
                 and words[j + 4:j + 4 + len(b)] == b
                 and (words[j + 2] << 16 | words[j + 3]) == len(b)]
            if not i:
                bad.append((label, 'atom name', a, b))
            continue
        unlfs, obj, at, status, tail, atail = got[label][-6:]
        if m.term(obj) != shown(b):
            bad.append((label, m.term(obj), shown(b)))
        if not (m.unbound(tail) and unlfs == tail and m.unbound(atail) and at == atail):
            bad.append((label, 'streams left', unlfs, tail, at, atail))
        if m.term(status) != 'normal':
            bad.append((label, m.term(status)))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    pinned = dict(PINNED)
    real = pinned.pop('real')
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep deca', pinned)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad or s.real != real:
        print('pimm lockstep deca: FAIL, %d real terms (pinned %d); answers differ: %r'
              % (s.real, real, bad[:3]))
        return 1
    names = sum(1 for w in want if w[1] == 'name')
    print('pimm lockstep deca: PASS (the IPL file decoder on atoms, lists and strings on '
          'the Bluespec core: %d terms, %d of them from the GC areas of the real '
          'pimm_kernel360E.sav, %d trace lines identical to the reference model; the '
          'test answers the reader\'s and the atom table\'s requests; every object as '
          'asm/unlsav.py reads the same words, and each of %d atom names handed over '
          'is the file\'s)' % (s.counts['parts'], s.real, s.counts['lines'], names))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
