#!/usr/bin/env python3
"""Lockstep: scsi_common:analyze_standard_format/5 from the IPL image.

    python3 ref/pimm/lockstep_asf.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_asf.py compare

Source (bios/scsi/scsi_common.kl1):

    analyze_standard_format(Valid,ErrClass,ErrCode,Sense,SenseData) :-
        Valid =:= 1 |
            get_4_bytes(Sense,0,Block,_),
            Block1 := 16#"1FF" /\\ Block,
            SenseData = nonextended(ErrorClass,ErrorCode,Block1).
    otherwise.
    analyze_standard_format(_,ErrClass,ErrCode,_,SenseData) :-
        true |
            SenseData = nonextended(ErrClass,ErrCode).

New here: write_variable (a structure element that is a new variable).
The first clause says ErrorClass and ErrorCode where the head says
ErrClass and ErrCode, so those two elements are fresh variables that
nothing binds; the object code agrees (write_variable r31, twice), and
so the answer for Valid = 1 is nonextended(_, _, Block1).  The first
predicate here that calls another (get_4_bytes/4) and leaves an answer
with a variable bound afterwards by a waiting built-in.

The oracle: the clauses above are asserted to be in the source text as
written here, and the answer is computed from them in Python, with
lockstep_get4's oracle (the source's own expression) for get_4_bytes.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  write_variable does not advance          case 0: the next cell written
  its register refers to the next cell     case 0: R 31
  it writes an integer cell                case 0: M 32808 00.. for 08..
Not caught by an answer, only by the trace: the register write_variable
sets is r31 both times here and nothing reads it.
"""
import io
import os
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driver  # noqa: E402
import lockstep_get4  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=9, lines=2632)

CLAUSES = '''analyze_standard_format(Valid,ErrClass,ErrCode,Sense,SenseData) :-
    Valid =:= 1 |
        get_4_bytes(Sense,0,Block,_),
        Block1 := 16#"1FF" /\\ Block,
        SenseData = nonextended(ErrorClass,ErrorCode,Block1).
otherwise.
analyze_standard_format(_,ErrClass,ErrCode,_,SenseData) :-
    true |
        SenseData = nonextended(ErrClass,ErrCode).'''

SENSES = [
    [0x12, 0x34, 0x56, 0x78, 0x9a],
    [0xff, 0xff, 0xff, 0xff],
    [0, 0, 1, 0],
    [0x80, 0x00, 0x00, 0x00],
]
# (Valid, ErrClass, ErrCode, sense index); Valid an integer or an atom
CASES = [(1, 7, 3, i) for i in range(len(SENSES))] + [
    (0, 7, 3, 0), (2, 1, 2, 1), (-1, 0, 0, 2), (('atom', 12), 5, 6, 0)]


def oracle():
    get4 = lockstep_get4.oracle()
    raw = subprocess.run(['gzip', '-dc', lockstep_get4.TAR], stdout=subprocess.PIPE,
                         check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('src/bios/scsi/scsi_common.kl1'):
                text = tf.extractfile(m).read().decode('latin1')

    def norm(s):
        return ' '.join(s.split())
    assert norm(CLAUSES) in norm(text), 'the clauses are not in the source as transcribed'

    def f(valid, eclass, ecode, sense):
        if valid == 1:                              # Valid =:= 1
            block = get4(sense, 0)                  # get_4_bytes(Sense,0,Block,_)
            return ('nonextended', None, None, 0x1ff & block)
        return ('nonextended', eclass, ecode)       # otherwise
    return f


def cell(v):
    return (pimm.ATOM, v[1]) if isinstance(v, tuple) else (pimm.INT, v & 0xffffffff)


def script():
    s = driver.Script()
    pc = pimm.predicate(pimm.kbndis.Image(), 'scsi_common', 'analyze_standard_format/5')
    want = []

    def goal(label, valid, eclass, ecode, si, late=False):
        s.label(label)
        s.string(0, 8, SENSES[si])
        s.newvar(1)
        if late:
            s.newvar(2)
            s.arg(1, 2)
        else:
            s.argc(1, cell(valid))
        s.argc(2, cell(eclass))
        s.argc(3, cell(ecode))
        s.arg(4, 0)
        s.arg(5, 1)
        s.spawn(pc, 5)
        s.run()
        if late:
            s.out(1)
            s.unifyc(2, cell(valid))
            s.run()
        s.out(1)
        want.append((label, valid, eclass, ecode, si))
    for i, (valid, eclass, ecode, si) in enumerate(CASES):
        goal('case %d: %r' % (i, (valid, eclass, ecode, si)), valid, eclass, ecode, si)
    goal('Valid bound late', 1, 4, 5, 0, late=True)
    return s, want


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep asf', PINNED)
    if not ok:
        return 1
    f = oracle()
    last = {}
    for label, w in s.outs:
        last[label] = w
    bad = []
    for label, valid, eclass, ecode, si in want:
        expect = f(valid if isinstance(valid, int) else 'atom', eclass, ecode, SENSES[si])
        got = m.term(last[label])
        if got != expect:
            bad.append((label, got, expect))
    if bad:
        print('pimm lockstep asf: FAIL, answers differ from the source: %r' % bad[:3])
        return 1
    print('pimm lockstep asf: PASS (scsi_common:analyze_standard_format/5 from the IPL '
          'image on the Bluespec core: %d goals, %d trace lines identical to the '
          'reference model; every answer the term the source gives, e.g. %r; %d '
          'built-in waits)' % (s.counts['parts'], s.counts['lines'],
                               m.term(last[want[0][0]]), m.builtin_waits))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
