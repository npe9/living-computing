#!/usr/bin/env python3
"""Lockstep: ipl_file_decoder:decode_0/7 from the IPL image, small integers.

    python3 ref/pimm/lockstep_dec0.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_dec0.py compare

ipl_file_decoder is the IPL's reader of unloader (.sav) files.  It is a
VARIANT of library/unloader/decoder.kl1, not that file compiled: 27 of
its 41 predicates have a source predicate of the same name and arity,
and where they can be compared several differ (set_status/3 has a
third behaviour, check_cdr/4 takes a vector for the status, the input
is not a list of words but requests the decoder makes).  So the source
is not used as a clause oracle here.

decode_0/7 is the source's decode/6 with the tag word already taken:

    decode_0(Tag, UNLFS0, UNLFS, Object, AT0, AT, Status)

(argument roles read from the image: decode_0/7 splits Tag into
Tag >> 8 and Tag /\\ 255 and calls decode_0/8, whose clauses for tags 1
and 2 unify as the source's decode_atomic/8 does.)  Only the two
one-word integer forms are asked here; they consume no input:

    01xx   the integer xx
    02xx   the integer xx \\/ 16#FFFFFF00

The oracle is asm/unlsav.py's parse_term on the same word, a decoder of
the format written independently from encoder.kl1; and the pass-through
of UNLFS0 to UNLFS and AT0 to AT, and Status = normal, as the format
needs.  New here: b_shift_right.  0200 is left out: the encoder never
writes it (encoder.kl1 encode_integer: 0 > N > 16#FFFFFF00), the image
and decoder.kl1 read it as -256 and unlsav.py as 0.  That a goal
whose tag comes late waits for it is checked by the trace only.  Other tags need instructions not
modelled yet (put_list, put_structured_constant, new_instruction).

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  shift_right shifts left           0100: R 1 = 10000 for 1
  shift_right operands swapped      0100: R 1 = 8 for 1
  shift_right one bit short         0100: R 1 = 2 for 1

Not caught: an arithmetic shift for the logical one.  Every tag here is
positive; a negative one leads to code not modelled yet.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import unlsav  # noqa: E402

PINNED = dict(parts=13, lines=1327)
TAGS = ([0x0100, 0x0101, 0x017f, 0x0180, 0x01fe, 0x01ff]
        + [0x0201, 0x027f, 0x0280, 0x02fe, 0x02ff])


def oracle(tag):
    kind, v = unlsav.parse_term(unlsav.Reader([tag]))
    assert kind == 'int'
    return v


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    pc = pimm.predicate(im, 'ipl_file_decoder', 'decode_0/7')
    want = []

    def goal(label, tag, late=False):
        # slots: 0 UNLFS, 1 Object, 2 AT, 3 Status, 4 the tag when late
        s.label(label)
        for i in range(4):
            s.newvar(i)
        if late:
            s.newvar(4)
            s.arg(1, 4)
        else:
            s.argc(1, (pimm.INT, tag))
        s.argc(2, (pimm.INT, 1111))
        s.arg(3, 0)
        s.arg(4, 1)
        s.argc(5, (pimm.INT, 2222))
        s.arg(6, 2)
        s.arg(7, 3)
        s.spawn(pc, 7)
        s.run()
        if late:
            s.out(1)
            s.unifyc(4, (pimm.INT, tag))
            s.run()
        for i in range(4):
            s.out(i)
        want.append((label, tag))

    for tag in TAGS:
        goal('%04x' % tag, tag)
    goal('01c8, tag late', 0x01c8, late=True)
    goal('0237, tag late', 0x0237, late=True)
    return s, want


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep dec0', PINNED)
    if not ok:
        return 1
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(m.term(w))
    bad = []
    for label, tag in want:
        expect = [1111, oracle(tag), 2222, 'normal']
        if got[label][-4:] != expect:
            bad.append((label, got[label][-4:], expect))
    if bad:
        print('pimm lockstep dec0: FAIL, answers differ from the format: %r' % bad[:3])
        return 1
    print('pimm lockstep dec0: PASS (ipl_file_decoder:decode_0/7 from the IPL image on '
          'the Bluespec core, one-word integers: %d goals, %d trace lines identical to '
          'the reference model; each object the integer asm/unlsav.py reads from the '
          'same word, e.g. %d for 02fe; input and atom table passed through)'
          % (s.counts['parts'], s.counts['lines'], oracle(0x02fe)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
