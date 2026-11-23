#!/usr/bin/env python3
"""Lockstep: the IPL loads a real object file with its own reader.

    python3 ref/pimm/lockstep_load.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_load.py compare

ipl_loader:load_file/9 (object code, asm/kl1decomp.py):

    load_file(normal(A), B, C, D, E, F, G, H, I) :- true |
        set_status(J, K, I),
        ipl_file_decoder:decode(L, B, C, M, D, E, H, K),
        calculate_priority_from_minimum(3900, N),
        decode_atom(M, F, G)@priority(N),
        read_unload_file(L, 0, "", 0, O, normal, J),
        double_buffer(A, O).

on pimm_patch_hash360E.sav, 1292 words.  Where lockstep_file.py played
the reader and the file's atom table, here both are the IPL's own
code:
  - double_buffer/2,4 asks the file for buffers (getb), two ahead;
  - read_unload_file/7, read_32/8, read_str/9 serve the decoder's
    three kinds of request from the buffers, and sum_check folds every
    buffer into the file's checksum (exclusive or of its 32-bit words,
    the halves folded: 0 for a good file; all 20 files held are good);
  - decode_atom/3,5 keeps the file's atom numbers in an ipl_pool
    (through a merger, lockstep_pool.py) and asks for each new name's
    atom with intern(Name, Atom).

The test stands in only for what is outside the IPL:
  - the file: each getb(R) is answered R = normal(a string of the
    next BUFFER 16-bit words).  The buffer size is OURS (the FEP's is
    not known); 97 is chosen so that a 32-bit request (read_32/8) and
    a string request (read_str/9) both fall across buffers, which the
    test checks by their code being run.  The getb asked ahead past
    the end of the file is never answered.
  - the atom table: intern(Name, Atom) is answered with 10000h + the
    number the file itself gives that name ([] for the name of nil),
    so that the module can be checked as in lockstep_newm.py.

Two runs:
  1. the file as it is: Status normal, the module object checked cell
     by cell (lockstep_newm.check_record), Info {FileName, []}, the
     interned names the file's own definitions in order;
  2. the file with its last word (the checksum) altered: Status is
     abnormal("CheckSum Error").

New on both models: string_operation in its binary form (the manual's
16 operations; the IPL uses 3, a copy), change_element_size, 32-bit
strings, the guards string_element and exclusive_or, b_exclusive_or;
and the first runs of set_nil and enqueue_goal_external.

Observed fault injections into the Bluespec, 2026-11-23, each FAILed
where shown and was restored:
All in the first run, at the trace line shown:
  change_element_size keeps the old type    1784: the new descriptor
  string operation 3 gives S1               11908: the word copied
  ... reads S2 from Pos1                    11908
  ... stops one element short               11913
  32-bit elements masked to 16              17431: the guard's element
  guard string_element takes the next       17431
  guard exclusive_or is an or               17455
  b_exclusive_or is an or                   18326
  enqueue_goal_external, one argument less  97: the record's count
  set_nil sets the next argument            265: A 6 for A 5

Not caught: change_element_size leaving the padding count 0 (the IPL
only widens to 32 bits, whose padding is 0).  Not run: the other 15
string operations as the IPL's code (only 3), narrowing, the forms of
string_operation with a vector of four or three, a file read error.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import unlsav  # noqa: E402
import lockstep_deca as deca  # noqa: E402
import lockstep_file as lfile  # noqa: E402
import lockstep_gca as gca  # noqa: E402
import lockstep_modc as modc  # noqa: E402
import lockstep_newm as newm  # noqa: E402

PINNED = dict(parts=2, lines=443348, cells=366, interned=13)
FILE = 'pimm_patch_hash360E.sav'
BUFFER = 97
MUST_RUN = ('read_32/8', 'read_str/9', 'sum_check/5', 'double_buffer/4', 'decode_atom/5')


def definitions(words):
    """[(number, name words)] of the file's atom definitions, in order."""
    out, inner = [], unlsav.read_atom_name

    def outer(r):
        i = r.i
        got = inner(r)
        if words[i] >= 0x8000:
            out.append((got[0], words[i + 3:r.i]))
        return got
    unlsav.read_atom_name = outer
    try:
        r = unlsav.Reader(words)
        _magic, nmod, _sep = r.rd(), r.rd(), r.rd()
        for _ in range(nmod):
            unlsav.parse_module(r)
    finally:
        unlsav.read_atom_name = inner
    return out


def run(s, im, names, words, defs, label):
    s.label(label)
    # 0 the file, 1 FileName, 2 Modules, 3 their tail, 4 Status,
    # 7 intern requests, 8 their tail, 9 Info, 10 normal(File)
    for i in (0, 1, 2, 3, 4, 7, 8, 9):
        s.newvar(i)
    s.vector(10, 11, [(pimm.ATOM, names['normal']), ('slot', 0)])
    for a, sl in ((1, 10), (2, 1), (4, 2), (5, 3), (6, 7), (7, 8), (8, 9), (9, 4)):
        s.arg(a, sl)
    s.argc(3, newm.PACKAGE)
    s.spawn(pimm.predicate(im, 'ipl_loader', 'load_file/9'), 9)
    feed, heard, byname = list(words), [], {tuple(n): k for k, n in defs}
    fs = ins = None
    while True:
        s.run()
        m = s.live()
        progress = False
        if fs is None:
            fs, ins = s.live_slot[0], s.live_slot[7]
        while feed:                         # the file
            w = m.deref(fs)
            if m.unbound(w) or w == (pimm.ATOM, 0):
                break
            req = m.deref((pimm.REF, w[1]))
            assert m.deref((pimm.REF, req[1])) == (pimm.ATOM, names['getb']), req
            chunk, feed = feed[:BUFFER], feed[BUFFER:]
            s.string(6, 16, chunk)
            s.vector(5, 13, [(pimm.ATOM, names['normal']), ('slot', 6)])
            s.setslot(15, (pimm.REF, req[1] + 1))
            s.unify(15, 5)
            fs = (pimm.REF, w[1] + 1)
            m = s.live()
            progress = True
        while True:                         # the atom table
            w = m.deref(ins)
            if m.unbound(w) or w == (pimm.ATOM, 0):
                break
            req = m.deref((pimm.REF, w[1]))
            assert m.deref((pimm.REF, req[1])) == (pimm.ATOM, names['intern']), req
            name = m.deref((pimm.REF, req[1] + 1))
            if m.unbound(name):
                break
            bits, elems = m.string(name)
            assert bits == 16
            heard.append(elems)
            n = byname[tuple(elems)]
            s.setslot(15, (pimm.REF, req[1] + 2))
            s.unifyc(15, (pimm.ATOM, 0 if elems == deca.NIL_NAME else 0x10000 + n))
            ins = (pimm.REF, w[1] + 1)
            m = s.live()
            progress = True
        if not progress:
            break
    s.setslot(6, ins)
    for i in (1, 2, 3, 4, 9, 6, 8):
        s.out(i)
    return len(feed), heard


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    words = lfile.file_words(FILE)
    defs = definitions(words)
    s = driver.Script()
    left, heard = run(s, im, names, words, defs, 'the file')
    bad = words[:-1] + [words[-1] ^ 0x0100]
    left2, _ = run(s, im, names, bad, defs, 'the checksum altered')
    want = dict(mods=modc.modules(FILE), tops=[a[3] for a in gca.areas(FILE)],
                left=(left, left2), heard=heard, defs=[n for _k, n in defs], im=im)
    return s, want


def check(s, m, want, ran):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad, cells = [], 0
    name, out, tail, status, info, ins, itail = got['the file'][-7:]
    if want['left'] != (0, 0):
        bad.append(('words not asked for', want['left']))
    if want['heard'] != want['defs']:
        bad.append(('interned', len(want['heard']), len(want['defs'])))
    if m.unbound(status) or m.term(status) != 'normal':
        bad.append(('status', None if m.unbound(status) else m.term(status)))
    else:
        iv = m.deref(info)
        if m.vsize(iv) != 2 or m.deref(m.mem[m.vbase(iv)]) != name \
                or m.deref(m.mem[m.vbase(iv) + 1]) != (pimm.ATOM, 0):
            bad.append(('Info',))
        if not (m.unbound(ins) and ins[1] == m.deref(itail)[1]):
            bad.append(('the intern requests do not end in their tail',))
        lst = m.deref(out)
        for mod, top in zip(want['mods'], want['tops']):
            if lst[0] & ~1 != pimm.LIST:
                bad.append(('modules list short',))
                break
            b, n = newm.check_record(m, mod, top, m.deref(m.mem[lst[1]]))
            cells += n
            bad += [(mod['name'], x) for x in b]
            lst = m.deref(m.mem[lst[1] + 1])
        if not (m.unbound(lst) and lst[1] == m.deref(tail)[1]):
            bad.append(('the list does not end in ModulesTail',))
    status2 = got['the checksum altered'][-4]
    text = 'CheckSum Error'
    if m.unbound(status2) or m.term(status2) != ('abnormal', (8, [ord(c) for c in text])):
        bad.append(('altered', None if m.unbound(status2) else m.term(status2)))
    missing = [p for p in MUST_RUN if p not in ran]
    if missing:
        bad.append(('not run', missing))
    return bad, cells


def ran_predicates(s, im):
    """The ipl_loader predicates whose code the reference run entered."""
    mod = [x for x in im.mods if x['name'] == 'ipl_loader'][0]
    spans = [(addr, addr + ln, name) for name, ln, addr in mod['preds']]
    ran = set()
    for line in s.all_lines:
        if line[0] == 'I':
            pc = int(line.split()[1])
            for lo, hi, name in spans:
                if lo <= pc < hi:
                    ran.add(name)
    return ran


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    s.all_lines = []
    play = s.play

    def keeping():
        for what, lines in play():
            s.all_lines += lines
            yield what, lines
    s.play = keeping
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep load',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, cells = check(s, m, want, ran_predicates(s, want['im']))
    if bad or cells != PINNED['cells'] or len(want['heard']) != PINNED['interned']:
        print('pimm lockstep load: FAIL %d cells, %d interned, %r'
              % (cells, len(want['heard']), bad[:3]))
        return 1
    print('pimm lockstep load: PASS (ipl_loader:load_file/9 on a real object file with the '
          "IPL's own reader, checksum and atom-number table, on the Bluespec core: %d trace "
          'lines identical to the reference model; the module object of %d cells as the '
          'file says, %d names interned in file order; the file with its checksum altered '
          'is refused with "CheckSum Error")' % (s.counts['lines'], cells, len(want['heard'])))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
