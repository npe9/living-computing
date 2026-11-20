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

The model is run for every 16-bit key and must agree with the oracle
on all 65,536; then for a non-integer argument (the otherwise clause)
and an unbound one (the goal must suspend).

Observed fault injections (2026-11-20), each restored afterwards:
  hash pair target one cell short        -> error: pc 9517 is not an
                                           instruction
  not_less_than operands swapped         -> FAIL, 62 keys wrong (the
                                           digits and letters gave '?')
  arithmetic result to the first operand -> FAIL, 62 keys wrong (2334
                                           gave 4, not '4')
  hash miss label relative to word 1     -> FAIL, 65,503 keys wrong
  hash index not key AND mask            -> FAIL, 32 keys wrong
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
    if ok:
        print('pimm jtoa: PASS (convert_element/2 from the IPL image agrees with '
              'its source on all 65536 keys, %d of them mapped; %d instructions)'
              % (hits, m.steps))
        return 0
    print('pimm jtoa: FAIL  %d keys wrong %s' % (len(wrong), note))
    for k, w, e in wrong[:8]:
        print('  key %04x: got %r, source says %d' % (k, w, e))
    return 1


if __name__ == '__main__':
    sys.exit(main())
