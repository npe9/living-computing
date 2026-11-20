#!/usr/bin/env python3
"""Lockstep: scsi_common:check_completion_code/4 from the IPL image.

    python3 ref/pimm/lockstep_ccode.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_ccode.py compare

The first predicate that builds structures.  Source
(bios/scsi/scsi_common.kl1):

    check_completion_code(_,CompletionCode,_,EResult) :-
        CompletionCode =:= 0 | EResult = normal.
    check_completion_code(_,CompletionCode,Detail,EResult) :-
        16#"8" =:= CompletionCode /\\ 16#"8" |
            EResult = abnormal(no_status(CompletionCode,Detail)).
    otherwise.
    check_completion_code(StatusByte,CompletionCode,Detail,EResult) :-
        true | EResult = abnormal(others(StatusByte,CompletionCode,Detail)).

New here: atoms (get_atom, write_atom), vectors of 2 to 4 cells
(put_vector_N, write_value; a term f(a,b) is the vector {f,a,b}),
get_bound_value, and the guards equal and and.

The oracle is those clauses, read from the source text in pimos.tar.Z:
each guard is rewritten as a Python expression and each body term is
parsed, so the expected answer is what the source says, as a nested
tuple; the result on the reference model is read back out of memory
(atoms by name through pimm_ipl.sym) and compared.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  get_atom's register from other bits      case 0: E fail for the bind
  write_atom writes an integer cell        case 0: M 32768 00.. for 02..
  equal as not-equal                       case 0: the second clause tried
  guard and as or                          case 1: R 4 = 9 for 0
  vector tag one size too large            case 1: R 4 = 1b.. for 19..
  write_value does not advance             case 1: the cell written
  put_vector takes one cell too few        case 1: the next vector's address
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
PINNED = dict(parts=17, lines=904)

# (StatusByte, CompletionCode, Detail); an integer or ('atom', number)
CASES = [(2, cc, 77) for cc in (0, 1, 7, 8, 9, 15, 16, 0x18, 0x7ff8, -1, -8, -9)] + [
    (0, 0, 0), (5, 8, ('atom', 12)), (6, 3, ('atom', 45)),
    (7, ('atom', 12), 1),          # not an integer: the otherwise clause
]


def parse_term(text, env):
    """A KL1 term of atoms, variables and f(args) as nested tuples."""
    text = text.strip()
    m = re.fullmatch(r'(\w+)\((.*)\)', text, re.S)
    if m:
        args, depth, cur = [], 0, ''
        for ch in m.group(2):
            if ch == ',' and depth == 0:
                args.append(cur)
                cur = ''
            else:
                depth += ch == '('
                depth -= ch == ')'
                cur += ch
        args.append(cur)
        return (m.group(1),) + tuple(parse_term(a, env) for a in args)
    return env[text] if text[0].isupper() or text[0] == '_' else text


def oracle():
    raw = subprocess.run(['gzip', '-dc', TAR], stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('src/bios/scsi/scsi_common.kl1'):
                text = tf.extractfile(m).read().decode('latin1')
    text = re.sub(r'%.*', '', text)
    clauses = re.findall(r'^check_completion_code\(([^)]*)\) :-\s*(.*?)\|\s*EResult = (.*?)\.\s*$',
                         text, re.M | re.S)
    assert len(clauses) == 3, clauses
    before = text.index('check_completion_code(StatusByte,CompletionCode,Detail,EResult) :-\n    true')
    assert 'otherwise.' in text[text.index('no_status'):before]

    def guard(g):
        g = re.sub(r'16#"([0-9A-Fa-f]+)"', r'0x\1', g.strip())
        g = g.replace('=:=', '==').replace('/\\', '&')
        return g if g != 'true' else 'True'

    def f(sb, cc, detail):
        for head, g, body in clauses:
            names = [h.strip() for h in head.split(',')]
            env = dict(zip(names, (sb, cc, detail, None)))
            py = guard(g)
            if py != 'True' and not isinstance(cc, int):
                continue                    # an arithmetic guard on a non-integer fails
            if eval(py, {'__builtins__': {}}, env):
                return parse_term(body, env)
        raise AssertionError('no clause')
    return f


def cell(v):
    return (pimm.ATOM, v[1]) if isinstance(v, tuple) else (pimm.INT, v & 0xffffffff)


def script():
    s = driver.Script()
    pc = pimm.predicate(pimm.kbndis.Image(), 'scsi_common', 'check_completion_code/4')
    for i, (sb, cc, det) in enumerate(CASES):
        s.label('case %d: %r' % (i, (sb, cc, det)))
        s.newvar(1)
        s.argc(1, cell(sb))
        s.argc(2, cell(cc))
        s.argc(3, cell(det))
        s.arg(4, 1)
        s.spawn(pc, 4)
        s.run()
        s.out(1)
    # CompletionCode unbound: the goal waits, then takes the second clause
    s.label('late')
    s.newvar(0)
    s.newvar(1)
    s.argc(1, cell(2))
    s.arg(2, 0)
    s.argc(3, cell(77))
    s.arg(4, 1)
    s.spawn(pc, 4)
    s.run()
    s.out(1)
    s.unifyc(0, cell(8))
    s.run()
    s.out(1)
    return s


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep ccode', PINNED)
    if not ok:
        return 1
    f = oracle()

    def name(v):
        return m.im.atom(v[1]) if isinstance(v, tuple) else v
    last = {}
    for label, w in s.outs:
        last[label] = w
    bad = []
    cases = [('case %d: %r' % (i, c), c) for i, c in enumerate(CASES)] + [('late', (2, 8, 77))]
    for label, (sb, cc, det) in cases:
        want = f(name(sb) if isinstance(sb, tuple) else sb,
                 cc if isinstance(cc, int) else name(cc), name(det))
        got = m.term(last[label])
        if got != want:
            bad.append((label, got, want))
    if bad:
        print('pimm lockstep ccode: FAIL, answers differ from the source: %r' % bad[:3])
        return 1
    print('pimm lockstep ccode: PASS (scsi_common:check_completion_code/4 from the IPL '
          'image on the Bluespec core: %d goals, %d trace lines identical to the '
          'reference model; every answer the term the source gives, e.g. %r)'
          % (s.counts['parts'], s.counts['lines'], m.term(last[cases[3][0]])))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
