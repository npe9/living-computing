#!/usr/bin/env python3
"""Lockstep: the console (display_console), by a file's name and comment.

    python3 ref/pimm/lockstep_cons.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_cons.py compare

display_console(X) "displays the current value of X on the console
window, even if this variable is unbound" (PDSS manual): 23:7F x, it
does not wait and cannot fail.  Here the console is the trace: a line
`C cell` with the dereferenced value and, for a string, a line
`S cell` for its descriptor and for each word.  How PIM/m's console
showed a value is not known; only what it was given is claimed.

The IPL's decoder (ipl_file_decoder:check_magic_num/13, object code)
shows, at priority 4096 through ipl:display_console/1 (convert/2 with
jis_to_ascii, then display_console_0/1):
  - for a file of magic 5702h, its COMMENT (the name is not shown);
  - for a file of magic 5502h, its NAME.

Two parts, decode/8 with the test as the reader (lockstep_deca.py):
  1. pimm_bios360E.sav (5702h), only up to the end of its comment: the
     console is given "PIMM BIOS       :3.600:25-Nov-93".  The modules
     are never fed, so the decoder's goals are left waiting (8).
  2. pimm_patch_hash360E.sav (5502h), whole, as lockstep_file.py but
     with FileName given: the console is given the name, Status is
     normal, and no further goal is left waiting (in lockstep_file.py
     the two display goals wait for the name for ever).  The name is
     the file's name in the archive; what the IPL's own file list
     called it is not held, so the name is OURS.

The oracle: the text is decoded from the trace's C and S lines and
compared with the file's comment words (and the name) put through
asm/psdpim.py's JIS table, which is not the IPL's converter.

Observed fault injections into the Bluespec, 2026-11-23, each FAILed
in part 1 at the trace line shown and was restored:
  the string's last word not shown       5465: the S line missing
  nothing shown for a string's cells     5457
  no C line                              5456
  the first word shown for every word    5459
NOT caught, because not run:
  register y taken, not x                both displays run are of
                                         register 0 (display_console_0's
                                         last clause); its list clause,
                                         register 1, is not run
  a non-string value fails the guard     only strings are displayed

The same wrong rule in BOTH models, tried on the reference model
alone, is reported by the text check: the descriptor only; one word
short; nothing displayed.

Not run: a non-string or unbound value; a list of strings; a clause
tried again after displaying (it would display again); the integers
pimos::top displays.  put_console, read_console, get_console and halt
are not implemented.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import psdpim  # noqa: E402
import lockstep_deca as deca  # noqa: E402
import lockstep_file as lfile  # noqa: E402
import lockstep_newm as newm  # noqa: E402

PINNED = dict(parts=2, lines=95614, waiting=8)
FILE = 'pimm_bios360E.sav'
FILE2 = 'pimm_patch_hash360E.sav'
# the second file's name in the archive; what the IPL's own file
# list called it is not held, so the name is OURS
NAME = 'pimm_patch_hash360E.sav'


def jis(text):
    """ASCII as two-byte JIS: row 23 letters and digits, row 21
    punctuation (the inverse of asm/psdpim.py's table)."""
    punct = {c: 0x2100 | k for k, c in psdpim.PUNCT.items()}
    return [0x2300 | ord(c) if c.isalnum() else punct[c] for c in text]


def ascii_of(words):
    """Two-byte JIS as ASCII, by asm/psdpim.py's table (row 23 the
    letters and digits, row 21 punctuation); not the IPL's converter."""
    out = ''
    for w in words:
        hi, lo = w >> 8, w & 0xff
        out += chr(lo) if hi == 0x23 else psdpim.PUNCT[lo]
    return out


def header(words):
    """(the words up to the end of the comment, the comment's words) of
    a 5702h file: magic, module count, FFFFh, a 32-bit length, text
    (library/unloader/encoder.kl1)."""
    assert words[0] == 0x5702 and words[2] == 0xffff
    n = words[3] << 16 | words[4]
    return words[:5 + n], words[5:5 + n]


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    head, comment = header(lfile.file_words(FILE))
    s.label('name and comment')
    # 0 In, 1 FileName, 2 Modules, 3 ModulesTail, 4 Status, 7 atom requests, 8 Info
    for i in (0, 2, 3, 4, 7, 8):
        s.newvar(i)
    s.string(1, 16, jis(NAME))
    s.arg(1, 0)
    s.arg(2, 1)
    s.argc(3, newm.PACKAGE)
    for a, sl in ((4, 7), (5, 2), (6, 3), (7, 8), (8, 4)):
        s.arg(a, sl)
    s.spawn(pimm.predicate(im, 'ipl_file_decoder', 'decode/8'), 8)
    s.live()
    at, feed = s.live_slot[0], list(head)
    while True:
        # the reader of lockstep_deca.serve, which stops when the head
        # of the file is used up: the modules are never read
        s.run()
        m = s.live()
        progress = False
        while feed:
            w = m.deref(at)
            if m.unbound(w) or w == (pimm.ATOM, 0):
                break
            if w[0] & ~1 == pimm.LIST:
                s.setslot(5, (pimm.REF, w[1]))
                s.unifyc(5, (pimm.INT, feed[0]))
                feed, at = feed[1:], (pimm.REF, w[1] + 1)
            elif w[0] & ~1 == pimm.VECT0 + 4:
                s.setslot(5, (pimm.REF, w[1]))
                s.unifyc(5, (pimm.INT, feed[0] << 16 | feed[1]))
                feed, at = feed[2:], (pimm.REF, w[1] + 1)
            elif w[0] & ~1 == pimm.VECT0 + 6:
                buf = m.deref((pimm.REF, w[1]))
                if m.unbound(buf):
                    break
                bits, elems = m.string(buf)
                assert bits == 16
                k = len(elems)
                s.string(6, 16, feed[:k])
                s.setslot(5, (pimm.REF, w[1] + 1))
                s.unify(5, 6)
                feed, at = feed[k:], (pimm.REF, w[1] + 2)
            else:
                raise AssertionError('an unknown request %r' % (w,))
            m = s.live()
            progress = True
        if not progress:
            break
    waiting = s.live().nsusp
    # a 5502h file, whole, as lockstep_file.py but with its name given
    words = lfile.file_words(FILE2)
    s.label('name')
    for i in (0, 2, 3, 4, 7, 8):
        s.newvar(i)
    s.string(1, 16, jis(NAME))
    s.arg(1, 0)
    s.arg(2, 1)
    s.argc(3, newm.PACKAGE)
    for a, sl in ((4, 7), (5, 2), (6, 3), (7, 8), (8, 4)):
        s.arg(a, sl)
    s.spawn(pimm.predicate(im, 'ipl_file_decoder', 'decode/8'), 8)
    s.live()
    names = {name: n for n, name in im.sym.items()}
    _at, _atq, feed2 = deca.serve(s, s.live_slot[0], s.live_slot[7], words, {}, names, [])
    s.out(4)
    return s, dict(left=(len(feed), len(feed2)), waiting=(waiting, s.live().nsusp),
                   text=[ascii_of(comment), NAME])


def console(lines):
    """What the trace says the console was given: a text for an 8-bit
    string, else the cell."""
    out, i = [], 0
    while i < len(lines):
        if lines[i][0] != 'C':
            i += 1
            continue
        cell = int(lines[i][2:], 16)
        i += 1
        cells = []
        while i < len(lines) and lines[i][0] == 'S':
            cells.append(int(lines[i][2:], 16))
            i += 1
        if cell >> 32 & ~1 != pimm.STRG:
            out.append(('cell', cell))
            continue
        desc = cells[0] & 0xffffffff
        typ, pad, words = desc >> 24 & 7, desc >> 27 & 3, desc & 0xffffff
        if cells[0] >> 32 != pimm.CDESC or typ != 3 or len(cells) != words + 1:
            out.append(('string', cells))
            continue
        raw = b''.join((c & 0xffffffff).to_bytes(4, 'big') for c in cells[1:])
        out.append(raw[:len(raw) - pad].decode('latin-1'))
    return out


def check(s, m, want, lines):
    bad = []
    got = console(lines)
    # the first file's modules are never fed; the second is read but
    # for its checksum, as in lockstep_file.py
    if want['left'] != (0, 1):
        bad.append(('words not asked for', want['left']))
    status = s.outs[-1][1]
    if m.unbound(status) or m.term(status) != 'normal':
        bad.append(('status of the second file',))
    # the second file leaves no goal waiting that the first had not
    if want['waiting'][0] != want['waiting'][1] or m.nsusp != want['waiting'][1]:
        bad.append(('goals waiting', want['waiting'], m.nsusp))
    if got != want['text']:
        bad.append(('console', got))
    return bad, got


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        m = s.live()
        lines = [x for _w, ls in s.play() for x in ls]
        print(check(s, s.machine, want, lines), s.machine.nsusp, len(lines))
        return 0
    s.all_lines = []
    play = s.play

    def keeping():
        for what, lines in play():
            s.all_lines += lines
            yield what, lines
    s.play = keeping
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep cons',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, got = check(s, m, want, s.all_lines)
    if bad or m.nsusp != PINNED['waiting']:
        print('pimm lockstep cons: FAIL %d waiting, %r' % (m.nsusp, bad[:3]))
        return 1
    print('pimm lockstep cons: PASS (display_console on the Bluespec core, %d trace lines '
          "identical to the reference model: the IPL's decoder shows a file's name and "
          'the comment of a real object file, %r)' % (s.counts['lines'], got))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
