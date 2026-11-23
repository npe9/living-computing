#!/usr/bin/env python3
"""Lockstep: scsi_common:analyze_request_sense_command_status1/6 from the IPL image.

    python3 ref/pimm/lockstep_rss.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_rss.py compare

Source (bios/scsi/scsi_common.kl1), asserted below to be in the text:

    analyze_request_sense_command_status1(Status,CompletionCode,Error,Header,Sense,SenseData) :-
        Status =:= 0,
        CompletionCode =:= 0,
        ErrClass := (Header >> 4) /\\ 16#"00000007",
        ErrCode  := Header /\\ 16#"0000000F",
        Valid    := (Header >> 7) /\\ 16#"00000001" |
            check_extended_format(ErrClass,ErrCode,Valid,Sense,SenseData).
    otherwise.
    analyze_request_sense_command_status1(Status,CompletionCode,Error,_,Sense,SenseData) :-
        true |
            SenseData = error_in_request_sense(Status,CompletionCode,Error,Sense).

    check_extended_format(7,0,Valid,Sense,SenseData) :-
        true |
            analyze_extended_format(Valid,ErrClass,ErrCode,Sense,SenseData).
    otherwise.
    check_extended_format(ErrClass,ErrCode,Valid,Sense,SenseData) :-
        true |
            analyze_standard_format(Valid,ErrClass,ErrCode,Sense,SenseData).

New here: the guard built-ins integer and shift_right (guard
arithmetic on the header), and put_vector_5.  A header of class 7,
code 0 goes to analyze_extended_format/5, which needs instructions not
modelled yet, and is not asked.  The answer for the other headers is
lockstep_asf's oracle for analyze_standard_format/5.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  integer passes anything bound        an atom for the header: the first clause goes on
  guard shift_right shifts left        header 83: R 6 = 830 for 8
  guard shift_right arithmetic         header ffffff0f: R 6 = fffffff0 for 0ffffff0
                                       (in the trace only; the mask hides it from the answer)
  guard shift_right writes r[x]        case 0: R 3 written for R 6
  put_vector_5 allocates four cells    case 10: the next goal's cells one lower
  put_vector_5 tagged as size 4        case 9: R 3 = 19.. for 1b..

Not caught: integer not noting an unbound operand.  The compiler puts a
wait before every integer here, so integer never sees one.
put_vector_1 and put_vector_6 are implemented alike and not run.
"""
import io
import os
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driver  # noqa: E402
import lockstep_asf  # noqa: E402
import lockstep_get4  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=19, lines=4756)
CLAUSES = __doc__[__doc__.index('    analyze_request_sense_command_status1('):
                  __doc__.index('New here:')].replace('\\\\', '\\')
SENSES = lockstep_asf.SENSES
ATOM = ('atom', 12)
# (Status, CompletionCode, Error, Header, sense index)
CASES = [
    (0, 0, 0, 0x00, 0), (0, 0, 0, 0x83, 0), (0, 0, 0, 0x9c, 1), (0, 0, 0, 0xef, 2),
    (0, 0, 0, 0x71, 3), (0, 0, 0, 0xf1, 0), (0, 0, 0, 0x60, 1), (0, 0, 9, 0x1a5, 2),
    (0, 0, 0, -1 & 0xffffff0f, 0),
    (2, 0, 0, 0x83, 0), (0, 5, 77, 0x83, 1), (30, 255, 65535, 0, 2),
    (0, 0, 3, ATOM, 0), (ATOM, 0, 0, 0x83, 0), (0, ATOM, 0, 0x83, 1),
]


def oracle():
    asf = lockstep_asf.oracle()
    raw = subprocess.run(['gzip', '-dc', lockstep_get4.TAR], stdout=subprocess.PIPE,
                         check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('src/bios/scsi/scsi_common.kl1'):
                text = tf.extractfile(m).read().decode('latin1')

    def norm(s):
        return ' '.join(s.split())
    for part in CLAUSES.split('\n\n'):
        assert norm(part) in norm(text), 'not in the source as transcribed: %s' % part[:60]

    def show(v):
        return 'normal' if v == ATOM else v

    def f(status, cc, error, header, sense):
        if status == 0 and cc == 0 and isinstance(header, int):
            h = header & 0xffffffff
            eclass, ecode, valid = (h >> 4) & 7, h & 15, (h >> 7) & 1
            assert (eclass, ecode) != (7, 0), 'analyze_extended_format is not modelled'
            return asf(valid, eclass, ecode, sense)
        return ('error_in_request_sense', show(status), show(cc), show(error), (8, list(sense)))
    return f


def cell(v):
    return (pimm.ATOM, v[1]) if isinstance(v, tuple) else (pimm.INT, v & 0xffffffff)


def script():
    s = driver.Script()
    pc = pimm.predicate(pimm.kbndis.Image(), 'scsi_common',
                        'analyze_request_sense_command_status1/6')
    want = []

    def goal(label, case, late=None):
        # slots: 0 the sense string, 1 SenseData, 2 a late variable
        s.label(label)
        s.string(0, 8, SENSES[case[4]])
        s.newvar(1)
        for i in range(4):
            if late == i:
                s.newvar(2)
                s.arg(i + 1, 2)
            else:
                s.argc(i + 1, cell(case[i]))
        s.arg(5, 0)
        s.arg(6, 1)
        s.spawn(pc, 6)
        s.run()
        if late is not None:
            s.out(1)
            s.unifyc(2, cell(case[late]))
            s.run()
        s.out(1)
        want.append((label, case))
    for i, case in enumerate(CASES):
        goal('case %d: %r' % (i, case), case)
    goal('status late', (0, 0, 0, 0x83, 0), late=0)
    goal('completion code late', (0, 0, 0, 0x9c, 1), late=1)
    goal('header late', (0, 0, 0, 0x25, 2), late=3)
    goal('header late, status not 0', (4, 0, 0, 0x25, 2), late=3)
    return s, want


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep rss', PINNED)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad:
        print('pimm lockstep rss: FAIL, answers differ from the source: %r' % bad[:3])
        return 1
    print('pimm lockstep rss: PASS (scsi_common:analyze_request_sense_command_status1/6 '
          'from the IPL image on the Bluespec core: %d goals, %d trace lines identical '
          'to the reference model; every answer the term the source gives, e.g. %r)'
          % (s.counts['parts'], s.counts['lines'], check.sample))
    return 0


def check(s, m, want):
    f = oracle()
    last = {}
    for label, w in s.outs:
        last[label] = w
    bad = []
    for label, case in want:
        expect = f(case[0], case[1], case[2], case[3], SENSES[case[4]])
        got = m.term(last[label])
        if got != expect:
            bad.append((label, got, expect))
    check.sample = m.term(last[want[10][0]])
    return bad


if __name__ == '__main__':
    sys.exit(main(sys.argv))
