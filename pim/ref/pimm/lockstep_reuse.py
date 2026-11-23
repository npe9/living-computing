#!/usr/bin/env python3
"""Lockstep: put_reused_structure of a vector of seven or more.

    python3 ref/pimm/lockstep_reuse.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_reuse.py compare
    python3 ref/pimm/lockstep_reuse.py --reference       the reference alone

put_reused_structure x, y, z: r[x] := a structure of z cells to be
filled by write_*, which the machine takes from r[y]'s cells when
nothing else refers to them.  Nothing is reused here (pimm.py
i_put_reused_structure): new cells, under the tag r[y]'s structure
has.  A vector of seven or more is {VECT, a} -> {VDESC, a + 3},
{INT, n}, {INT, n} and the elements (pimm.py vsize), so the new one
gets a descriptor of its own.  Fewer than seven cells under a long
vector's tag is refused by both models.

The image's one such site, scsi_fep_file:request_device_io/6 at 3826
(asm/kl1decomp.py):

    request_device_io({201, A, B, C, D, E, F}, G, H, I, J, K) :- true |
        set_vector_element({201, A, B, C, D, E, F}, 6, 0, L, M),
        J = [id(N, O)|P], K = {Q, R},
        request_device_io(L, G, H, I, P, R),
        device_create(M, I, N, O, Q).
    device_create({201, A, B, C, D, E, _}, F, G, H, I) :- wait(G), integer(G) |
        I = [send({G, 201, F, A, B, C}, J)|K],
        check_send_status(J, D, G, H, K, {G, E}).

One part, the bench answering as the IPL's other processes would:
  create    the message {201, 11, 12, 13, 14, E, 0}, a vector of seven
            the bench makes cell by cell (descriptor, two lengths,
            elements), with G unbound, I = 9.  The message is rebuilt
            (put_reused_structure 0, 0, 7 and seven write_*), its
            element 6 taken out and replaced by 0.  Element 6 was 0
            (no further message): J = [id(N, O)], H = 0, R = [].  The
            bench binds N = 4: Q = [send({4, 201, 9, 11, 12, 13},
            S)|T]; the bench binds S = abnormal: T = [] and E = 5
            (scsi_fep_util:device_abnormal/1 on {4, E}).
            Expected, from the source above: J = [id(4, _)],
            K = {[send({4, 201, 9, 11, 12, 13}, abnormal)], []},
            E = 5, H = 0, G unbound; and the message as the bench
            holds it is {201, 11, 12, 13, 14, 5, 0}, untouched but for
            E.  The elements 1..3 in `send` and E come from the
            REBUILT vector.

Observed fault injections into the Bluespec (bsv/PimmStages.bsv),
2026-11-23, each restored from a copy:
  no descriptor, seven cells under the long tag (as before)  line 71
  the structure pointer at the descriptor                    line 76
  the register points at the first element                   line 74
  the new vector's MRB off whatever the old one's            line 74
NOT caught:
  the new vector tagged by the vector box (MRB on) and not by the
  old vector's tag: the old one's MRB is on here, as it is for every
  argument the bench gives

Not run: a reused long vector reached with every MRB off (the bench's
argument is always marked, so set_vector_element copies again); any
size but seven (the image's one site); the refusal.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=1, lines=396)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
SITE = 3826


def var_at(m, a):
    """A reference to the unbound variable the cell at a is or leads to."""
    c = m.mem[a]
    if c[0] & ~1 in (pimm.UNDF, pimm.HOOK):
        return (pimm.REF, a)
    w = m.deref(c)
    assert m.unbound(w), w
    return w


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    assert im.dis(SITE).startswith('put_reused_structure 0,0,7')
    s = driver.Script()

    s.label('create')
    # a vector of seven: ten cells in a row, slots 2..11
    for k in range(10):
        s.newvar(2 + k)
    s._op(driver.PTR, 0, 2, (pimm.VECT0 + 15, 0))
    m = s.live()
    base = s.live_slot[2][1]
    assert [s.live_slot[2 + k][1] for k in range(10)] == [base + k for k in range(10)]
    s.unifyc(2, (pimm.VDESC, base + 3))
    s.unifyc(3, I(7))
    s.unifyc(4, I(7))
    for k, v in enumerate((201, 11, 12, 13, 14, None, 0)):
        if v is not None:
            s.unifyc(5 + k, I(v))                  # E: slot 10
    for k in (12, 13, 14, 15):                     # G, H, J, K
        s.newvar(k)
    s.arg(1, 0)
    s.arg(2, 12)
    s.arg(3, 13)
    s.argc(4, I(9))
    s.arg(5, 14)
    s.arg(6, 15)
    s.spawn(pimm.predicate(im, 'scsi_fep_file', 'request_device_io/6'), 6)
    s.run()
    m = s.live()
    assert m.term(s.live_slot[0]) == (201, 11, 12, 13, 14, None, 0)
    # N: element 1 of id(N, O), the car of J
    j = m.deref(s.live_slot[14])
    ident = m.deref(m.mem[j[1]])
    s.setslot(1, var_at(m, ident[1] + 1))
    s.unifyc(1, I(4))
    s.run()
    m = s.live()
    # S: element 2 of send(.., S), the car of Q, element 0 of K
    k = m.deref(s.live_slot[15])
    q = m.deref(m.mem[k[1]])
    send = m.deref(m.mem[q[1]])
    s.setslot(1, var_at(m, send[1] + 2))
    s.unifyc(1, A('abnormal'))
    s.run()
    for slot in (14, 15, 10, 13, 12, 0):
        s.out(slot)
    return s


WANT = [[('id', 4, None)],
        ([('send', (4, 201, 9, 11, 12, 13), 'abnormal')], []),
        5, 0, None, (201, 11, 12, 13, 14, 5, 0)]


def check(s, m, parts):
    bad = []
    got = [None if m.unbound(w) else m.term(w) for _label, w in s.outs]
    if got != WANT:
        bad.append((got, WANT))
    lines = parts.get('create', [])
    if 'E fail' in lines:
        bad.append(('a reduction failed',))
    # the site is taken once, and a descriptor is written after it: a
    # {VDESC, the cell three on}
    at = [k for k, ln in enumerate(lines) if ln.startswith('I %d ' % SITE)]
    if len(at) != 1:
        bad.append(('the site taken %d times' % len(at),))
    else:
        f = lines[at[0] + 1].split()
        if f[0] != 'M' or int(f[2][:2], 16) != pimm.VDESC \
                or int(f[2][2:], 16) != m.load + int(f[1]) + 3:
            bad.append(('no descriptor after the site', lines[at[0] + 1]))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        parts = dict(s.play())
        print(check(s, s.machine, parts), len(parts), sum(len(v) for v in parts.values()))
        return 0
    kept = {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            yield what, lines
    s.play = keeping
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep reuse',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(s, m, kept)
    if bad:
        print('pimm lockstep reuse: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep reuse: PASS (put_reused_structure of a vector of seven on the '
          'Bluespec core, %d trace lines identical to the reference model: '
          'scsi_fep_file:request_device_io/6 rebuilds a create message with a descriptor of '
          'its own, the bench answers id and send, and the answers are the source\'s)'
          % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
