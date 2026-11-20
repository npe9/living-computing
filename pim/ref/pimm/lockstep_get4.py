#!/usr/bin/env python3
"""Lockstep: scsi_common:get_4_bytes/4 from the IPL image.

    python3 ref/pimm/lockstep_get4.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_get4.py compare

get_4_bytes(S, From, Int, NS) (bios/scsi/scsi_common.kl1) reads four
string elements from From and combines their low bytes, first element
highest.  As compiled, the second to fourth string_element are reached
before their index (From+1 ..) has been computed: each waits as a goal
of its stub, on an index it then receives through get_value.  New
here: b_and, b_or, b_shift_left, and a built-in with two outputs
waiting.

The oracle is the source's own expression: the `Int := ...` clause is
taken from the source text in pimos.tar.Z, its KL1 operators rewritten
as Python's, and evaluated on the four elements.

Scenarios: 8-bit strings at every offset that fits; a 16-bit string
whose elements have high bytes (which the expression masks off); a
first byte >= 0x80 (a negative integer); From unbound until after the
goal has started.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  Exec  b_and computes or               string 0 from 0: R 0 = ff for 12
  Exec  b_or computes and               string 0 from 0: R 3 = 0 for 1234
  Exec  shift_left operands swapped     string 0 from 0: R 0 = 200000 for 1200
"""
import io
import os
import re
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driver  # noqa: E402
import pimm  # noqa: E402

TAR = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'pimos.tar.Z')
PINNED = dict(parts=11, lines=4960)

STRINGS = [
    (8, [0x12, 0x34, 0x56, 0x78, 0x9a, 0xbc, 0xde, 0xf0]),
    (8, [0xff, 0xff, 0xff, 0xff]),
    (8, [0, 0, 0, 0, 1]),
    (16, [0xa512, 0x0034, 0xff56, 0x1278, 0x8001]),
]


def oracle():
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('src/bios/scsi/scsi_common.kl1'):
                text = tf.extractfile(m).read().decode('latin1')
    clause = re.search(r'^get_4_bytes\(S,From,Int,NS\) :-(.*?)\.\s*$', text, re.M | re.S).group(1)
    # the four elements are read from From, From+1, From+2, From+3 in order
    idx = re.findall(r'string_element\(\w+,\s*(~\(From\+\d\)|From),\s*(\w+),', clause)
    assert [i for i, _v in idx] == ['From', '~(From+1)', '~(From+2)', '~(From+3)'], idx
    names = [v for _i, v in idx]
    expr = re.search(r'Int := (.*)', clause, re.S).group(1)
    expr = re.sub(r'16#"([0-9A-Fa-f]+)"', r'0x\1', expr)
    expr = expr.replace('/\\', '&').replace('\\/', '|')
    assert re.fullmatch(r'[\w\s()&|<]+', expr), expr

    def f(elems, start):
        env = dict(zip(names, elems[start:start + 4]))
        return eval(expr, {'__builtins__': {}}, env) & 0xffffffff
    return f


def script():
    s = driver.Script()
    pc = pimm.predicate(pimm.kbndis.Image(), 'scsi_common', 'get_4_bytes/4')
    want = []           # (label, string index, from)

    def goal(si, bits, elems, start, late):
        label = 'string %d from %d%s' % (si, start, ' (From bound late)' if late else '')
        s.label(label)
        s.string(0, bits, elems)
        s.newvar(1)                 # Int
        s.newvar(2)                 # NS
        s.arg(1, 0)
        if late:
            s.newvar(3)
            s.arg(2, 3)
        else:
            s.argc(2, (pimm.INT, start))
        s.arg(3, 1)
        s.arg(4, 2)
        s.spawn(pc, 4)
        s.run()
        if late:
            s.out(1)
            s.unifyc(3, (pimm.INT, start))
            s.run()
        s.out(1)
        s.out(2)
        want.append((label, si, start))

    for si, (bits, elems) in enumerate(STRINGS):
        for start in range(len(elems) - 3):
            goal(si, bits, elems, start, False)
    goal(0, 8, STRINGS[0][1], 2, True)
    return s, want


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep get4', PINNED)
    if not ok:
        return 1
    f = oracle()
    outs = {}
    for label, w in s.outs:
        outs.setdefault(label, []).append(w)
    bad = []
    for label, si, start in want:
        bits, elems = STRINGS[si]
        got_int, got_ns = outs[label][-2], outs[label][-1]
        if got_int != (pimm.INT, f(elems, start)):
            bad.append((label, got_int, f(elems, start)))
        elif got_ns[0] & ~1 != pimm.STRG or m.string(got_ns) != (bits, elems):
            bad.append((label, 'NS', got_ns))
    if bad:
        print('pimm lockstep get4: FAIL, answers differ from the source: %r' % bad[:3])
        return 1
    print('pimm lockstep get4: PASS (scsi_common:get_4_bytes/4 from the IPL image on '
          'the Bluespec core: %d goals, %d trace lines identical to the reference '
          'model; answers as the source expression gives; %d built-in waits)'
          % (s.counts['parts'], s.counts['lines'], m.builtin_waits))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
