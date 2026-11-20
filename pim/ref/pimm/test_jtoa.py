#!/usr/bin/env python3
"""jis_to_ascii:convert_element/2, run from the IPL image, against its source.

The object code is the predicate in pimm_ipl.kbn; the machine is
ref/pimm/pimm.py.  The oracle is built from two PIMOS source texts and
nothing else:

  bios/boot/jtoa.kl1         the predicate: three range clauses, 33
                             `Elem = #"X" | EElem = c#"Y"` clauses, and
                             `otherwise` giving c#"?"
  server/telnet/code_cv.kl1  table_ascii_to_jis/2, PIMOS's own table
                             for what 16-bit JIS code #"X" is

convert_element/2 is run for every 16-bit key and must agree with the
oracle on all 65,536; then for a non-integer argument (the otherwise
clause) and an unbound one (the goal must suspend).

convert/2 (which calls convert_loop/4 and convert_element/2) is then
run on 16-bit strings: empty, one element, every mapped key, a mixed
one, and "PIMOS 3.6" in full-width characters.  Each result must be the
8-bit string the oracle gives; set_string_element must have waited
once per element (it is reached before its element is bound); an 8-bit
argument must fail; an unbound argument must suspend the goal and
complete after the variable is bound.

Observed fault injections (2026-11-20), each restored afterwards:
  hash pair target one cell short        -> error: pc 9517 is not an
                                           instruction
  not_less_than operands swapped         -> FAIL, 62 keys wrong (the
                                           digits and letters gave '?')
  arithmetic result to the first operand -> FAIL, 62 keys wrong (2334
                                           gave 4, not '4')
  hash miss label relative to word 1     -> FAIL, 65,503 keys wrong
  hash index not key AND mask            -> FAIL, 32 keys wrong
 on convert/2:
  string_element's two outputs swapped   -> error: not a string
  binding does not wake waiting goals    -> error: 1 goals still suspended
  goal arguments taken from slot 0       -> error: unify of two different
                                           strings
  string/3 length and size swapped       -> error: no clause of convert/2
                                           applies
  make_string packing from the bottom    -> FAIL, 4 of 5 strings wrong
  guard `subtract` writing its first
  operand instead of its third           -> PASS: NOT caught.  The only
                                           use is `subtract 0,4,0`, where
                                           the two are the same register;
                                           the destination reading is
                                           unverified by a run (the
                                           compiler source gives it:
                                           asm/bltdir.py).
 on the runtime state in cells (goal records, hooks, stubs):
  woken goal not put on the ready queue  -> error: 93 goals still suspended
  binding wakes nothing                  -> error: 1 goals still suspended
  goal arguments taken from slot 0       -> error: unify of two different
                                           strings
  waiting built-in's output register not
  given its variable                     -> FAIL, 4 of 5 strings wrong
  waiting built-in's goal one cell into
  its stub                               -> error: pc 18372 is not an
                                           instruction
 on string packing:
  elements packed from the bottom of the
  word, in reading and writing alike     -> FAIL: the image's strings read
                                           'ellI lag LPIeliF'.  Only the
                                           image-string check sees this;
                                           every conversion still agrees.
"""
import io
import os
import re
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pimm  # noqa: E402

TAR = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'pimos.tar.Z')


def sources():
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE,
                         check=True).stdout
    out = {}
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            for want in ('src/bios/boot/jtoa.kl1', 'src/server/telnet/code_cv.kl1'):
                if m.name.endswith(want):
                    out[want] = tf.extractfile(m).read().decode('latin1')
    return out['src/bios/boot/jtoa.kl1'], out['src/server/telnet/code_cv.kl1']


def oracle():
    jtoa, code_cv = sources()
    a2j = dict((int(a), int(j, 16)) for a, j in re.findall(
        r'^table_ascii_to_jis\((\d+),Jis\):- true \| Jis=16#"([0-9A-Fa-f]+)"',
        code_cv, re.M))
    # #"X" | c#"Y" clauses; a doubled quote inside the string is one quote
    pairs = re.findall(r'Elem = #"(""|.)" \|\s*EElem = c#"(""|.)"\.', jtoa)
    assert len(pairs) == 33, len(pairs)
    table = {}
    for x, y in pairs:
        table[a2j[ord(x[0])]] = ord(y[0])
    ranges = re.findall(r'Elem >= #"(.)",\s*#"(.)" >= Elem \|[^\n]*\n\s*'
                        r'EElem := c#"(.)" \+ \(Elem - #"(.)"\)\.', jtoa)
    assert len(ranges) == 3, ranges
    default = re.search(r'otherwise\.\s*convert_element\(Elem,EElem\) :-\s*'
                        r'true \|\s*EElem = c#"(.)"\.', jtoa).group(1)

    def f(k):
        for lo, hi, base, lo2 in ranges:        # clause order as written
            if a2j[ord(lo)] <= k <= a2j[ord(hi)]:
                return ord(base) + (k - a2j[ord(lo2)])
        if k in table:
            return table[k]
        return ord(default)
    return f, len(table)


def main():
    f, nsym = oracle()
    m = pimm.Machine()
    pc = pimm.predicate(m.im, 'jis_to_ascii', 'convert_element/2')
    wrong = []
    hits = 0
    for k in range(0x10000):
        out = m.new_var()
        m.run(pc, [(pimm.INT, k), out])
        w = m.deref(out)
        if w != (pimm.INT, f(k)):
            wrong.append((k, w, f(k)))
        hits += f(k) != ord('?')
    ok = not wrong
    # a non-integer first argument: only the otherwise clause applies
    out = m.new_var()
    m.run(pc, [(pimm.ATOM, 5), out])
    ok &= m.deref(out) == (pimm.INT, ord('?'))
    # an unbound first argument: no clause can be chosen yet
    try:
        m.run(pc, [m.new_var(), m.new_var()])
        ok = False
        note = 'unbound argument did not suspend'
    except pimm.Suspend:
        note = ''
        m.abandon()
    # ---- convert/2: the whole module, strings in and out ----------
    conv = pimm.predicate(m.im, 'jis_to_ascii', 'convert/2')
    mapped = [k for k in range(0x10000) if f(k) != ord('?')]
    cases = [[], [0x2350], mapped, mapped[::-1] + [0x3021, 0, 0xffff],
             [0x2350, 0x2349, 0x234d, 0x234f, 0x2353, 0x2121, 0x2333, 0x2125, 0x2336]]
    cwrong = []
    waits0 = m.builtin_waits
    for jis in cases:
        out = m.new_var()
        m.run(conv, [m.make_string(16, jis), out])
        w = m.deref(out)
        got = m.string(w) if w[0] & ~1 == pimm.STRG else w
        if got != (8, [f(k) for k in jis]):
            cwrong.append((jis[:4], got))
    last = bytes(got[1]) if not cwrong else b''
    # In convert_loop/4 set_string_element is reached before
    # convert_element has bound its element: the built-in must wait.
    bwaits = m.builtin_waits - waits0
    ok &= not cwrong and last == b'PIMOS 3.6' and bwaits == sum(map(len, cases))
    # an 8-bit string is not string(JIS,_,16): no clause applies
    try:
        m.run(conv, [m.make_string(8, [65]), m.new_var()])
        ok = False
        note += ' 8-bit string did not fail'
    except pimm.Fail:
        pass
    # an unbound string: the goal suspends, and runs when it is bound
    sv, out = m.new_var(), m.new_var()
    try:
        m.run(conv, [sv, out])
        ok = False
        note += ' unbound string did not suspend'
    except pimm.Suspend:
        m.unify(sv, m.make_string(16, [0x2341, 0x2342]))
        m.run()
        w = m.deref(out)
        ok &= w[0] & ~1 == pimm.STRG and m.string(w) == (8, [65, 66])
    if not ok:
        print('pimm jtoa: convert/2: %d cases wrong, %d built-in waits %s'
              % (len(cwrong), bwaits, note))
        for c in cwrong[:3]:
            print('  %r' % (c,))
    # String packing, against constants in the image itself: the IPL's
    # message strings must read as text (elements from the top of each
    # word; a 16-element and a 25-element one, so with and without pad).
    def text(cell):
        size, elems = m.string(m.im.cells[cell])
        return size, bytes(elems).decode('latin1')
    if text(1860) != (8, 'Illegal IPL File') or text(1896) != (8, 'Unable to Decode Constant'):
        ok = False
        note += ' image strings %r %r' % (text(1860), text(1896))
    if ok:
        print('pimm jtoa: PASS (from the IPL image: convert_element/2 agrees with its '
              'source on all 65536 keys, %d mapped; convert/2 on %d strings, '
              '%d built-in waits; %d instructions, %d reductions)'
              % (hits, len(cases), bwaits, m.steps, m.reductions))
        return 0
    print('pimm jtoa: FAIL  %d keys wrong %s' % (len(wrong), note))
    for k, w, e in wrong[:8]:
        print('  key %04x: got %r, source says %d' % (k, w, e))
    return 1


if __name__ == '__main__':
    sys.exit(main())
