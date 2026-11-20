#!/usr/bin/env python3
"""Which operands of a built-in instruction are inputs and which outputs.

PIMOS's KL1 compiler holds the table: library/compiler/blt.kl1 has one
builtin/9 clause per guard built-in and one active_builtin/6 clause per
body built-in.  Each names the instruction it emits (`Y=subtract(Y1,
Y2,Y3)`), the operands read (`In=[X1,Y1,X2,Y2]`) and those written
(`Out=[X3,Y3]`).  This reads those clauses out of pimos.tar.Z and gives
each instruction a direction string, one letter per operand in the
order the instruction carries them: i = read, o = written, ? = named
in neither list.

    python3 asm/bltdir.py            the table
    python3 asm/bltdir.py --check    pinned counts and readings

It settles what object code alone cannot: in the IPL's jis_to_ascii
the only guard `subtract` is `subtract 0,4,0`, where reading the first
or the third operand as the destination gives the same result.  The
table says iio.

The comparison operators are there too: `X1 >= X2` emits
not_less_than(Y1,Y2) and `X1 =< X2` emits not_less_than(Y2,Y1), so
not_less_than a,b is a >= b.

Caveat: the source is the 1992 release; the binaries are 1994.
"""
import io
import os
import re
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
TAR = os.path.join(HERE, '..', 'docs', 'nonlocal', 'pimos.tar.Z')

PINNED = dict(guard=87, body=120, parsed_guard=87, parsed_body=120,
              unknown_operands=0)
PINNED_DIRS = {
    ('guard', 'subtract'): 'iio',
    ('guard', 'string'): 'ioo',
    ('guard', 'not_less_than'): 'ii',
    ('guard', 'less_than'): 'ii',
    ('body', 'b_subtract'): 'iio',
    ('body', 'b_add'): 'iio',
    ('body', 'new_string'): 'iio',
    ('body', 'b_string_element'): 'iioo',
    ('body', 'set_string_element'): 'iiio',
}


def source():
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE,
                         check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('src/library/compiler/blt.kl1'):
                return tf.extractfile(m).read().decode('latin1')
    raise KeyError('blt.kl1')


def table(text=None):
    text = text if text is not None else source()
    text = re.sub(r'%.*', '', text)
    out = []
    count = dict(guard=0, body=0)
    for kind, head in (('guard', 'builtin'), ('body', 'active_builtin')):
        for m in re.finditer(r'^%s\((.*?),\s*Y\s*,\s*In\b(.*?)\.\s*$'
                             % head, text, re.M | re.S):
            count[kind] += 1
            body = m.group(2)
            y = re.search(r'\bY\s*=\s*(\w+)(?:\(([^)]*)\))?', body)
            ins = re.search(r'\bIn\s*=\s*\[([^\]]*)\]', body)
            outs = re.search(r'\bOut\s*=\s*\[([^\]]*)\]', body)
            if not (y and ins and outs):
                continue
            operands = [a.strip() for a in (y.group(2) or '').split(',') if a.strip()]
            iv = set(re.findall(r'\bY\d+\w*', ins.group(1)))
            ov = set(re.findall(r'\bY\d+\w*', outs.group(1)))
            d = ''.join('i' if a in iv else 'o' if a in ov else '?' for a in operands)
            out.append((kind, y.group(1), d, re.sub(r'\s+', '', m.group(1))))
    return out, count


def main(argv):
    rows, count = table()
    got = dict(guard=count['guard'], body=count['body'],
               parsed_guard=sum(r[0] == 'guard' for r in rows),
               parsed_body=sum(r[0] == 'body' for r in rows),
               unknown_operands=sum(r[2].count('?') for r in rows))
    if '--check' not in argv:
        for kind, name, d, src in rows:
            print('%-5s %-40s %-8s %s' % (kind, name, d, src))
        print(got)
        return 0
    dirs = {(k, n): d for k, n, d, _s in rows}
    bad = [(k, dirs.get(k), v) for k, v in PINNED_DIRS.items() if dirs.get(k) != v]
    if got != PINNED or bad:
        print('bltdir: FAIL  %r (pinned %r) %r' % (got, PINNED, bad))
        return 1
    print('bltdir: PASS (%d guard and %d body built-ins, every operand '
          'marked input or output by the compiler source)'
          % (got['parsed_guard'], got['parsed_body']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
