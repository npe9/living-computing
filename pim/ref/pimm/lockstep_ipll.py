#!/usr/bin/env python3
"""Lockstep: the IPL reads its file list, the real pimos.ipl.

    python3 ref/pimm/lockstep_ipll.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_ipll.py compare

ipl:boot0 calls ipl_files(FileReq, "pimos:pimos.ipl", OpenRequests,
Files) (docs/binary_reverse_engineering.md 1.3).  By its object code
(asm/kl1decomp.py ipl): on FileReq = normal(Req) it sends
open(Name, R) as the first request, takes R = normal(F), reads F with
getb(R1) requests, each answered normal(Buffer) until end_of_file,
joins the buffers (append_string/3) and cuts the text into names
(decompose/2: at code 10; JIS percent, 2173h, to the end of the line
is a comment; nothing empty is kept).  The requests after the open
are OpenRequests, which ipl_loader:load/4 then uses.

The list is the REAL one: object/pimos.ipl in
docs/nonlocal/pimosobj.tar.Z, 1678 bytes of two-byte JIS, read out of
the archive when the test runs.  The test stands in for what answers
the requests (the IPL's SCSI file service, not run); a getb is
answered with 256 words, which is OURS.

Two parts:
  the list   the held pimos.ipl: twenty names, the eight system files
             then the twelve patches, each a full path
             (>sys>csp>PIMOS.DIR>pimm_kernel360E.sav first).
  comments   a list of OURS with a comment line, a comment after a
             name, an empty line and no line end at the end (the held
             list has none of these): a.sav, b.sav, c.sav.
Checked: the open request's name; the number of getb requests; Files
against the manual's rule applied in Python (by_hand: e-sysman.tex,
"one path a line", "a percent sign" comment), which is not the IPL's
code; the request list goes on into OpenRequests; the list's stream
is closed; no goal left waiting.

No machine rule is new here: every instruction this takes was in, so
no fault was injected for it.  What it adds is the check of the
IPL's own code against the real list.

Not run: an open that fails (abnormal), a read error; the names are
not then given to load/4 in this test (lockstep_link.py gives its
own).  The heap this takes, 867,326 cells for 839 words, is
set_string_element copying the whole string for each element moved
(gap_analysis B8).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_cons as cons  # noqa: E402

PINNED = dict(parts=2, lines=951364, files=20)
ARCHIVE = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'pimosobj.tar.Z')
MEMBER = 'object/pimos.ipl'
LIST = 'pimos:pimos.ipl'
# A list of OURS for what the held one has none of: a comment line, a
# comment after a name, an empty line, no line end at the end.
OURS = (cons.jis('a.sav') + [10, 0x2173] + cons.jis('note') + [10, 10] + cons.jis('b.sav')
        + [0x2173] + cons.jis('tail') + [10] + cons.jis('c.sav'))
CHUNK = 256          # words a getb is answered with: OURS (the FEP's is not known)


def list_words():
    """The 16-bit words of pimos.ipl as held."""
    z = subprocess.run(['zcat'], stdin=open(ARCHIVE, 'rb'), stdout=subprocess.PIPE, check=True)
    b = subprocess.run(['tar', '-xOf', '-', MEMBER], input=z.stdout, stdout=subprocess.PIPE,
                       check=True).stdout
    assert len(b) == 1678
    return [int.from_bytes(b[i:i + 2], 'big') for i in range(0, len(b), 2)]


def by_hand(words):
    """The entries, by the manual's rule (e-sysman.tex: one path a line,
    a percent sign starts a comment) applied here in Python: split at
    code 10, cut at JIS percent (2173h), drop what is empty."""
    out, line = [], []
    for w in words + [10]:
        if w == 10:
            if 0x2173 in line:
                line = line[:line.index(0x2173)]
            if line:
                out.append(line)
            line = []
        else:
            line.append(w)
    return out


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    s = driver.Script()
    return s, [one(s, im, A, 'the list', list_words()), one(s, im, A, 'comments', OURS)]


def one(s, im, A, label, words):
    s.label(label)
    # ipl_files(normal(Req), "pimos:pimos.ipl", OpenRequests, Files)
    s.vector(0, 4, [A('normal'), None])            # Req in slot 5
    s.string(1, 16, cons.jis(LIST))
    s.newvar(2)
    s.newvar(3)
    for a in (1, 2, 3, 4):
        s.arg(a, a - 1)
    s.spawn(pimm.predicate(im, 'ipl', 'ipl_files/4'), 4)
    s.run()
    m = s.live()
    # Req = [open(Name, R) | OpenRequests]
    w = m.deref(s.live_slot[5])
    assert w[0] & ~1 == pimm.LIST, w
    req = m.deref((pimm.REF, w[1]))
    asked = m.term(req)[:2]
    s.newvar(8)
    s.vector(9, 11, [A('normal'), ('slot', 8)])
    s.setslot(15, (pimm.REF, req[1] + 2))
    s.unify(15, 9)
    s.setslot(7, (pimm.REF, w[1] + 1))             # the tail: OpenRequests
    s.run()
    m = s.live()
    at, feed, gets = s.live_slot[8], list(words), 0
    while True:
        # [getb(R) | More]: R = normal(Buffer), or end_of_file
        w = m.deref(at)
        if m.unbound(w) or w == (pimm.ATOM, 0):
            break
        req = m.deref((pimm.REF, w[1]))
        assert m.deref((pimm.REF, req[1])) == A('getb'), req
        gets += 1
        s.setslot(15, (pimm.REF, req[1] + 1))
        if feed:
            chunk, feed = feed[:CHUNK], feed[CHUNK:]
            s.string(6, 16, chunk)
            s.vector(5, 13, [A('normal'), ('slot', 6)])
            s.unify(15, 5)
        else:
            s.unifyc(15, A('end_of_file'))
        at = (pimm.REF, w[1] + 1)
        s.run()
        m = s.live()
    s.setslot(4, at)
    s.out(3)
    s.out(7)
    s.out(2)
    s.out(4)
    return dict(label=label, asked=asked, gets=gets, left=len(feed), words=words,
                waiting=s.live().nsusp)


def check(s, m, wants):
    bad, files = [], []
    for want in wants:
        b, f = check_one(s, m, want)
        bad += [(want['label'],) + x for x in b]
        files.append(f)
    return bad, files


def check_one(s, m, want):
    bad = []
    files, tail, opens, stream = [w for l, w in s.outs if l == want['label']][-4:]
    if want['asked'] != ('open', (16, cons.jis(LIST))):
        bad.append(('asked', want['asked']))
    if want['left'] or want['gets'] != (len(want['words']) + CHUNK - 1) // CHUNK + 1:
        bad.append(('getb requests', want['gets'], want['left']))
    got = None if m.unbound(files) else m.term(files)
    exp = [(16, line) for line in by_hand(want['words'])]
    if got != exp:
        bad.append(('Files', str(got)[:200]))
    # the request list goes on into OpenRequests; the list's stream is closed
    if not (m.unbound(tail) and m.unbound(opens) and tail[1] == opens[1]):
        bad.append(('the requests after open', tail, opens))
    if m.deref(stream) != (pimm.ATOM, 0):
        bad.append(('the stream is not closed', stream))
    if want['waiting']:
        bad.append(('%d goals left waiting' % want['waiting'],))
    return bad, [cons.ascii_of(x[1]) for x in got or []]


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        n = sum(len(ls) for _w, ls in s.play())
        bad, files = check(s, s.machine, want)
        print(bad, n, s.machine.hp - s.machine.load)
        print(files[1], len(files[0]))
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep ipll',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, files = check(s, m, want)
    if bad or len(files[0]) != PINNED['files'] or files[1] != ['a.sav', 'b.sav', 'c.sav']:
        print('pimm lockstep ipll: FAIL %r, %r' % (files[1], bad[:3]))
        return 1
    print("pimm lockstep ipll: PASS (ipl:ipl_files/4 on the Bluespec core reads the held "
          'pimos.ipl: %d trace lines identical to the reference model; %d file names, the '
          'first %r, the last %r)' % (s.counts['lines'], len(files[0]), files[0][0], files[0][-1]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
