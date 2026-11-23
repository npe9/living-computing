#!/usr/bin/env python3
"""Lockstep: the IPL file decoder on whole real object files.

    python3 ref/pimm/lockstep_file.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_file.py compare

ipl_file_decoder:decode/8, the predicate the IPL's loader calls for a
file (ipl_loader:load_file/9, object code:

    load_file(normal(A), B, C, D, E, F, G, H, I) :- true |
        ipl_file_decoder:decode(L, B, C, M, D, E, H, K),
        decode_atom(M, F, G)@priority(N), read_unload_file(L, ...), ...

so decode(In, FileName, Package, AtomRequests, Modules, ModulesTail,
Info, Status)), given every word of a real file of the PIM/m object
set, from the magic number to the atom table at the end:

    pimm_patch_hash360E.sav    1292 words, 1 module    (this test)
    pimm_patch_shutl360E.sav   7139 words, 3 modules   (lockstep_file3.py:
                               the same test; the two do not fit one
                               heap, which only grows)

Path: decode/8 -> check_magic_num/13 (a goal of 13 arguments: three
packed in a vector, lockstep_pack.py) -> load_modules/8 -> per module
load_module/7 and ipl_module:load/4 -> decode_atom_table/4.

Checked, per file:
  - Status is normal; Info is {FileName, []} (magic 5502h: no comment);
  - Modules is one module(Package, Name, Module, ExternalModules) per
    module of the file, in file order, ending in ModulesTail; each
    module object is checked cell by cell as in lockstep_newm.py
    (check_record), against asm/unlsav.py's reading of the file;
  - the input stream is closed after the atom table's count, with ONE
    word of the file unread (the last: the loader's sum check reads
    it, ipl_loader:sum_check), and the atom requests are closed.

Stand-ins, as in lockstep_deca.py: the test plays the reader and the
atom table.  The atom table's last request is put_all(Names, Status);
every file held ends with an empty table (a count of 0), which the
IPL's own handler answers with Status = normal when no get is waiting
(ipl_loader:decode_atom/5, put_all_atom/6, resume_get/3, object code).
A file with names in that table is not played.

New on both models:
  set_atom N            23:00..0F: goal argument N := the atom
                        (assembler/inst_tab.kl1)
  calculate_priority_from_minimum(X, ^Y)   22:ED.  "The logical
                        priority corresponding to X is calculated from
                        the logical priority range for the shoen", X in
                        0..4096 (manual).  No shoen here: the range is
                        taken as 0..4096, Y = X.  The range is OURS.
  enqueue_goal_with_priority  23:64, two cells: the priority's
                        register, the label, and the arity in the next
                        cell's top byte (assembler/klb_opr.kl1
                        p(r_c16_c8_exe); all five sites in the image
                        agree with their set_* count).  The priority
                        must be an integer and is DROPPED: one ready
                        queue here, a goal stack per priority on the
                        machine.  So the ORDER goals run in is not the
                        machine's.

What is left waiting: check_magic_num/13 makes $bar0(FileName) at
priority 4096, which is ipl:display_console(FileName): the file's
name on the console.  FileName is given unbound here, so that goal
waits and nothing is displayed; console output is not modelled yet.
Files with magic 5702h carry a comment that is displayed likewise;
none is run here.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
All in this test, at the trace line shown:
  set_atom sets the next argument          117: A 2 for A 1
  set_atom sets the atom plus one          117: the atom
  enqueue_goal_with_priority steps one     267: runs the arity cell
    cell
  ... takes the arity from x               265: the record's count
  calculate_priority gives twice           258: R 0 2000h for 1000h
  the spread of 13 arguments stops short   98: A 13 not written

Not caught: calculate_priority_from_minimum writing its operand's
register (both sites here use one register for both).  The priority's
VALUE is checked only as the two models agreeing: nothing reads it.
"""
import io
import os
import struct
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_deca as deca  # noqa: E402
import lockstep_gca as gca  # noqa: E402
import lockstep_modc as modc  # noqa: E402
import lockstep_newm as newm  # noqa: E402

PINNED = dict(parts=1, lines=90250, cells=366)
FILES = ('pimm_patch_hash360E.sav',)
NAME = 'file'


def file_words(fname):
    raw = subprocess.run(['gzip', '-dc', deca.OBJ], stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('/' + fname):
                data = tf.extractfile(m).read()
    return list(struct.unpack('>%dH' % (len(data) // 2), data))


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    names = {name: n for n, name in im.sym.items()}
    want = []
    for fname in FILES:
        words = file_words(fname)
        assert words[0] == 0x5502 and words[2] == 0xffff, fname
        mods = modc.modules(fname)
        tops = [a[3] for a in gca.areas(fname)]
        assert words[1] == len(mods) == len(tops)
        s.label(fname)
        # 0 In, 1 FileName, 2 Modules, 3 ModulesTail, 4 Status, 7 atom requests, 8 Info
        for i in (0, 1, 2, 3, 4, 7, 8):
            s.newvar(i)
        s.arg(1, 0)
        s.arg(2, 1)
        s.argc(3, newm.PACKAGE)
        for a, sl in ((4, 7), (5, 2), (6, 3), (7, 8), (8, 4)):
            s.arg(a, sl)
        s.spawn(pimm.predicate(im, 'ipl_file_decoder', 'decode/8'), 8)
        s.live()
        at, atq, feed = deca.serve(s, s.live_slot[0], s.live_slot[7], words, {}, names, [])
        s.setslot(9, at)
        s.setslot(10, atq)
        for i in (1, 2, 3, 4, 8, 9, 10):
            s.out(i)
        want.append((fname, mods, tops, len(feed)))
    return s, want


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad, cells = [], 0
    for fname, mods, tops, left in want:
        name, out, tail, status, info, at, atq = got[fname][-7:]
        if left != 1:
            bad.append((fname, '%d words left' % left))
        if m.unbound(status) or m.term(status) != 'normal':
            bad.append((fname, 'status'))
            continue
        if at != (pimm.ATOM, 0) or atq != (pimm.ATOM, 0):
            bad.append((fname, 'streams not closed', at, atq))
        iv = m.deref(info)
        if m.vsize(iv) != 2 or m.deref(m.mem[m.vbase(iv)]) != name or not m.unbound(name) \
                or m.deref(m.mem[m.vbase(iv) + 1]) != (pimm.ATOM, 0):
            bad.append((fname, 'Info'))
        lst = m.deref(out)
        for mod, top in zip(mods, tops):
            if lst[0] & ~1 != pimm.LIST:
                bad.append((fname, 'modules list short'))
                break
            b, n = newm.check_record(m, mod, top, m.deref(m.mem[lst[1]]))
            cells += n
            bad += [(fname, mod['name'], x) for x in b]
            lst = m.deref(m.mem[lst[1] + 1])
        if not (m.unbound(lst) and lst[1] == m.deref(tail)[1]):
            bad.append((fname, 'the list does not end in ModulesTail'))
    return bad, cells


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep %s' % NAME,
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, cells = check(s, m, want)
    if bad or cells != PINNED['cells']:
        print('pimm lockstep %s: FAIL %d cells, %r' % (NAME, cells, bad[:3]))
        return 1
    print('pimm lockstep %s: PASS (ipl_file_decoder:decode/8 on %d whole real object '
          'file, %d modules, on the Bluespec core: %d trace lines identical to the '
          'reference model; every module comes out as a module object, %d cells each as '
          'the file says, and one word of each file, its checksum, is left unread)'
          % (NAME, len(FILES), sum(len(w[1]) for w in want), s.counts['lines'], cells))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
