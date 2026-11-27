#!/usr/bin/env python3
"""SIMPOS methods MENDELS's ESP half needs (psi/mendels.py, 2026-11-27),
as kl0 models (Python): stand-ins, NOT SIMPOS, whose classes are lost.
Each has its grade below or in its docstring.

1. simpos##standard_io_buffer's text methods.  The class's slots and
creator are the stand-in psi/standin/standard_io_buffer.esp.

PRINTED, the 1990 ESP manual (IFS manuals/esp ESPtex program-e.tex
6733-6745, program-j.tex 6470-6480, Example 3 "Conversion between string
(heap) and global stack"):

    ?- :create(#standard_io_buffer,B).
    ?- :putl(B,"p(1,2)."),:putl(B,"[1,2].").
    ?- :gett(B,CP).          CP= p(1,2)
    ?- :gett(B,List).        List= [1,2]
    ?- :putt(B,[1,2]), :putt(B,p(1,2)).
    ?- :getl(B,S)            S= "[1,2]p(1,2)"

(the manual's `put1`/`get1` are putl/getl in the TeX's font, as every
held caller spells them).  So what putl and putt write is what gett and
getl read: one buffer, written at its end and read from its front.
INFERENCE from the example: putl/2 ends the line it writes (a newline
after the string: `p(1,2).` then `[1,2].` must read as two terms, and the
end `.` needs layout after it), and gett/2 takes the one layout character
after a term's `.` with it (as a Prolog read does), so the getl/2 after
the two putt/2s reads "[1,2]p(1,2)", not the empty rest of a line.

INFERENCE from the held caller, MENDELS esp_device.esp:146-170 (to_string/
3, to_term/3) and esp_util.esp:28-33: `:reset(B)` empties the buffer
before a conversion and `:reread(B)` is sent between the writes and the
reads; here reset empties the text and its read position, reread puts
the read position back to the front (OURS: in the printed example the
reads follow the writes with no reread, so a write is readable at once
here too).

INFERENCE from the same caller: a term is read from text with no ending
`.`: MENDELS converts "start", "load_library", ... (main.kl1 call_loop/3,
esp_device.esp esp_control/2), strings with no period, by putl then
gett, on both sides; here the end of the text ends the last term.

The writer (putt) is OURS: integers in decimal, atoms bare (quoted when
they are not a plain name), strings in double quotes, lists [..], and a
vector whose first element is an atom and which has more elements as
F(A, ...), as the printed p(1,2) (a compound term is a vector in KL0,
psi/esp_reader.py's convention); any other vector {..}.  A variable is
written _ (OURS).  The reader is psi/esp_reader.py's (OURS).
"""
import re

import esp_reader

NAME = re.compile(r'^[a-z][A-Za-z0-9_]*$')


def write(K, t):
    t = K.deref(t)
    if isinstance(t, K.Var):
        return '_'
    if isinstance(t, bool):
        raise K.Refusal('simpos', 'standard_io_buffer putt/2 of %r' % (t,))
    if isinstance(t, int):
        return str(t)
    if isinstance(t, K.Str):
        return '"%s"' % t.text.replace('"', '""')
    if isinstance(t, K.Atom):
        if t is K.NIL or t.name == '[]':
            return '[]'
        return t.name if NAME.match(t.name) else "'%s'" % t.name.replace("'", "''")
    if isinstance(t, K.Cons):
        items = []
        while isinstance(t, K.Cons):
            items.append(write(K, t.args[0]))
            t = K.deref(t.args[1])
        tail = '' if (isinstance(t, K.Atom) and t.name == '[]') else '|' + write(K, t)
        return '[%s%s]' % (','.join(items), tail)
    if isinstance(t, K.Vec):
        el = [K.deref(e) for e in t.elements()] if hasattr(t, 'elements') else [K.deref(e) for e in t.args]
        if len(el) > 1 and isinstance(el[0], K.Atom) and el[0].name != '[]':
            return '%s(%s)' % (write(K, el[0]), ','.join(write(K, e) for e in el[1:]))
        return '{%s}' % ','.join(write(K, e) for e in el)
    raise K.Refusal('simpos', 'standard_io_buffer putt/2 of %r' % (t,))


def read_one(K, text):
    """(term, rest) of TEXT: the first term, ended by `.` or by the
    text's end (module doc).  None when TEXT holds no term."""
    toks = esp_reader.tokens(text)
    if not toks:
        return None
    j = 0
    while j < len(toks) and toks[j][0] != 'end':
        j += 1
    r = esp_reader.Reader(K, toks[:j])
    t = r.term(1200)
    if r.i != len(r.t):
        raise ValueError('reader: trailing %r' % (r.t[r.i:],))
    # the rest of the text after the term's end: found again by its tokens
    # (OURS: the text after the `.`, or nothing)
    if j == len(toks):
        return t, ''
    n = 0
    pos = 0
    while n <= j:
        mt = esp_reader.TOKEN.match(text, pos)
        pos = mt.end()
        if mt.lastgroup != 'ws':
            n += 1
    # the layout character after the `.` goes with it (module doc)
    if text[pos:pos + 1].isspace():
        pos += 1
    return t, text[pos:]


# The label of each model's behaviour (agent_rules.md; test_mendels
# test_models_labelled checks every model installed has one):
# RECONSTRUCTED-FROM-MANUAL: the ESP manual's Example 3 (module doc)
LABELS = {
    ('simpos##standard_io_buffer', 'instance', 'putl', 2): 'RECONSTRUCTED-FROM-MANUAL (the newline INFERENCE)',
    ('simpos##standard_io_buffer', 'instance', 'putt', 2): 'RECONSTRUCTED-FROM-MANUAL (the writer OURS)',
    ('simpos##standard_io_buffer', 'instance', 'gett', 2): 'RECONSTRUCTED-FROM-MANUAL (the end-of-text term INFERENCE; the reader OURS)',
    ('simpos##standard_io_buffer', 'instance', 'getl', 2): 'RECONSTRUCTED-FROM-MANUAL',
    ('simpos##standard_io_buffer', 'instance', 'reset', 1): 'INFERENCE',
    ('simpos##standard_io_buffer', 'instance', 'reread', 1): 'INFERENCE',
    ('simpos##symbolizer', 'class', 'is_object', 2): 'INFERENCE',
    ('simpos##library_utility', 'instance', 'get_packages_with_wildcard', 3): 'INFERENCE',
    ('simpos##library_utility', 'instance', 'get_classes', 4): 'INFERENCE',
    ('simpos##library_utility', 'instance', 'get_classes_with_wildcard', 5): 'INFERENCE',
    ('simpos##library_utility', 'class', 'loading_lines', 3): 'OURS (the line HELD-SOURCE)',
    ('simpos##process', 'instance', 'refute_in', 5): 'INFERENCE (the catchers not installed: OURS)',
}


def install(models, K):
    """Add the buffer's text methods to kl0's SIMPOS_MODELS."""
    C = 'simpos##standard_io_buffer'

    def text(m, b):
        t = K.deref(m.get_slot(b, 'text'))
        return t.text if isinstance(t, K.Str) else ''

    def set_text(m, b, s, pos=None):
        v = K.Str('')
        v.text = s
        m.set_slot(b, 'text', v)
        if pos is not None:
            m.set_slot(b, 'position', pos)

    def recv(m, n):
        b = K.deref(m.x[n])
        if not isinstance(b, K.Instance):
            raise K.Refusal('simpos', 'standard_io_buffer: receiver %r' % (b,))
        return b

    def string_arg(m, i, what):
        s = K.deref(m.x[i])
        if not isinstance(s, K.Str):
            raise K.Refusal('unbound argument' if isinstance(s, K.Var) else 'simpos',
                            'standard_io_buffer %s of %r' % (what, s))
        return s.text

    def reset(m):
        set_text(m, recv(m, 0), '', 0)
        m.proceed()

    def reread(m):
        m.set_slot(recv(m, 0), 'position', 0)
        m.proceed()

    def putl(m):
        b = recv(m, 1)
        set_text(m, b, text(m, b) + string_arg(m, 0, 'putl/2') + '\n')
        m.proceed()

    def putt(m):
        b = recv(m, 1)
        set_text(m, b, text(m, b) + write(K, m.x[0]))
        m.proceed()

    def unread(m, b):
        return text(m, b)[K.deref(m.get_slot(b, 'position')):]

    def gett(m):
        b = recv(m, 1)
        rest = unread(m, b)
        try:
            got = read_one(sys_K(), rest)
        except ValueError as e:
            raise K.Refusal('simpos', 'standard_io_buffer gett/2: %s' % e)
        if got is None:
            return m.fail()
        t, after = got
        m.set_slot(b, 'position', len(text(m, b)) - len(after))
        return m.proceed() if m.unify(m.x[0], t) else m.fail()

    def getl(m):
        b = recv(m, 1)
        rest = unread(m, b)
        line, _nl, after = rest.partition('\n')
        m.set_slot(b, 'position', len(text(m, b)) - len(after))
        v = K.Str('')
        v.text = line
        return m.proceed() if m.unify(m.x[0], v) else m.fail()

    def sys_K():
        return K

    def is_object(m):
        """:is_object(#symbolizer, X): X is an object (an instance or a
        class).  INFERENCE from MENDELS's use: esp_device.esp to_string/3
        and to_term/3 test a slot that holds 0 until a buffer is made,
        loader.esp load_MENDEL/2 a window slot; the name and the receiver
        are the held send's.  OURS that it never raises"""
        v = K.deref(m.x[0])
        return m.proceed() if isinstance(v, (K.Instance, K.ClassRef)) else m.fail()

    models[('simpos##symbolizer', 'class', 'is_object', 2)] = is_object

    # 2. library_utility's queries (standin/library_utility.esp's head
    # comment has the sources): over kl0's library, ids the atoms
    # pkg##class, in the library's order (OURS)
    def klist(items):
        out = K.NIL
        for x in reversed(items):
            out = K.Cons(x, out)
        return out

    def name_of(m, i, what):
        v = K.deref(m.x[i])
        if isinstance(v, K.Str):
            return v.text
        if isinstance(v, K.Atom):
            return v.name
        raise K.Refusal('unbound argument' if isinstance(v, K.Var) else 'simpos',
                        'library_utility %s: argument %d is %r' % (what, i + 1, v))

    def kind_all(m, i, what):
        v = K.deref(m.x[i])
        if not (isinstance(v, K.Atom) and v.name == 'all'):
            raise K.Refusal('simpos', 'library_utility %s: kind %r (only all is modelled)' % (what, v))

    def packages(m, pattern):
        import fnmatch
        seen = []
        for cid in m.lib.templates:
            p = cid.split('##', 1)[0]
            if p not in seen and fnmatch.fnmatchcase(p, pattern):
                seen.append(p)
        return seen

    def classes(m, pkg, pattern='*'):
        import fnmatch
        return [K.Atom(c) for c in m.lib.templates
                if c.split('##', 1)[0] == pkg and fnmatch.fnmatchcase(c.split('##', 1)[1], pattern)]

    def get_packages_with_wildcard(m):
        pk = [K.Atom(p) for p in packages(m, name_of(m, 0, 'get_packages_with_wildcard/3'))]
        return m.proceed() if m.unify(m.x[1], klist(pk)) else m.fail()

    def get_classes(m):
        kind_all(m, 1, 'get_classes/4')
        ids = classes(m, name_of(m, 0, 'get_classes/4'))
        return m.proceed() if m.unify(m.x[2], klist(ids)) else m.fail()

    def get_classes_with_wildcard(m):
        kind_all(m, 2, 'get_classes_with_wildcard/5')
        ids = classes(m, name_of(m, 0, 'get_classes_with_wildcard/5'),
                      name_of(m, 1, 'get_classes_with_wildcard/5'))
        return m.proceed() if m.unify(m.x[3], klist(ids)) else m.fail()

    def loading_lines(m):
        """:loading_lines(#library_utility, Ids, Lines): OURS helper of
        load/2, the COPY's `Loading <id>...` line per id (ds_bep.esp:1992)"""
        ids, out, t = [], [], K.deref(m.x[0])
        while isinstance(t, K.Cons):
            ids.append(K.deref(t.args[0]))
            t = K.deref(t.args[1])
        for i in ids:
            if not isinstance(i, K.Atom):
                raise K.Refusal('simpos', 'library_utility load/2: id %r' % (i,))
            v = K.Str('')
            v.text = 'Loading %s...' % i.name
            out.append(v)
        return m.proceed() if m.unify(m.x[1], klist(out)) else m.fail()

    # 3. process refute_in/5
    def refute_in(m):
        """:refute_in(Process, Catchers, Obj, Method, Args): the dynamic
        call :Method(Obj, Args...) (class `class`'s refute/3, kl0
        Machine.refute) with a catcher for the events of the classes
        listed (USAGE: shell.md §2.10, kappa2 HLCMNG.ESP:212-222, MENDELS
        esp_device.esp:20-21; the catcher's meaning INFERENCE there).
        OURS: the catchers are not installed, so an event the call raises
        goes on to kl0's own handling, a refusal; none is raised on this
        run's path"""
        method, args, obj = m.x[2], m.x[3], m.x[1]
        m.x[0], m.x[1], m.x[2] = method, args, obj
        return m.refute()

    models[('simpos##process', 'instance', 'refute_in', 5)] = refute_in

    U = 'simpos##library_utility'
    models[(U, 'instance', 'get_packages_with_wildcard', 3)] = get_packages_with_wildcard
    models[(U, 'instance', 'get_classes', 4)] = get_classes
    models[(U, 'instance', 'get_classes_with_wildcard', 5)] = get_classes_with_wildcard
    models[(U, 'class', 'loading_lines', 3)] = loading_lines
    models[(C, 'instance', 'reset', 1)] = reset
    models[(C, 'instance', 'reread', 1)] = reread
    models[(C, 'instance', 'putl', 2)] = putl
    models[(C, 'instance', 'putt', 2)] = putt
    models[(C, 'instance', 'gett', 2)] = gett
    models[(C, 'instance', 'getl', 2)] = getl
