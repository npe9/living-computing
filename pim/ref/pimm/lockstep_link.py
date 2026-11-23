#!/usr/bin/env python3
"""Lockstep: the IPL's whole loader, ipl_loader:load/4, on a file list.

    python3 ref/pimm/lockstep_link.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_link.py compare

load(Files, OpenRequests, Close, Loaded) is what ipl:boot0 calls
after it has read the file list (docs/binary_reverse_engineering.md
1.3).  By its object code (asm/kbndis.py ipl_loader load/4,
load_files/10, check_link_status/5, check_module/7): it starts the
atom table (lockstep_atab.py) and the link table
(ipl_link_table:link/1), shows "IPL loading", then for each file
name sends open(Name, R) on OpenRequests, takes R = normal(File) and
loads it with load_file/9 (lockstep_load.py); after the last it shows
"Link Modules ...", sends link(Status) to the link table, and on a
normal status looks for the boot module and its predicate
(predicate_to_code).  Loaded is the answer.

Two parts, each a list of ONE file:
  load         pimm_patch_hash360E.sav, whose module hasher calls
               pool_usage, which is not loaded;
  six modules  pimm_patch_mkdir360E.sav (41,359 words, six modules,
               sixteen modules called and not held).  Several of its
               modules name the same external module, so the linker's
               put_ex_mod/8 sends get_and_put(A, {B, H}, {B, [D|H]})
               and two vectors are unified (lockstep_unif.py): 23
               times, three steps each, counted.  The heap passes
               2^20 cells in this part (1,509,638 at the end).  The test stands in for
what answers OpenRequests (the IPL's SCSI file service, not run) and
for the file's buffers.  The file's name is its name in the archive:
OURS, the IPL's own list (pimos.ipl) is not played.

Checked:
  - one open request, with the name given;
  - the console is given "IPL loading", the file's name, "Link
    Modules ..." (the last is the line the PIMOS manual's boot log
    shows, e-sysman.tex);
  - Loaded = abnormal(["Undefined Module Found", Name]), Name ONE
    module the file calls and does not hold: the linker stops at the
    first it meets (ipl_link_table:resolve_2/9 as decompiled by
    asm/kl1decomp.py: "resolve_2(yes, A, ...) :- B = [], C =
    abnormal([string8#"Undefined Module Found", A])").  This file
    has only one, pool_usage, by asm/unlsav.py's reading
    (lockstep_gca.areas).  The second part's file has sixteen and
    one of them is reported, fep_file_device.
  - the file is read to its last word; no goal is left waiting.

New on both models: the guard atom (a type test).  Also new, for the
bench: SETW fills a string the bench has made in place, where SETEL
went through set_string_element and copied the string per element;
every test that builds a string has a shorter trace for it, and trace
line numbers quoted in headers written before 2026-11-23 are as
observed then.

Observed fault injections into the Bluespec, 2026-11-23, restored:
  atom guard fails on an atom          link: line 196757
  bench fill: the next word written    conv: part 1, line 2
NOT caught: atom guard succeeds on a non-atom (the guard is only run
on atoms).  In the reference model alone, as if in both: "atom
always fails" is reported (Loaded unbound, 6 goals waiting); "atom
always succeeds" passes, for the same reason.

Memory, 2026-11-23: 2^26 cells (it was 2^20); the Bluespec loads only
the 2^15 cells below the heap from its file.  Injections, restored:
  heap addresses wrap at 2^20          link: part 1, line 6148480
  the image RAM is one bit too small   conv: part 1, line 141
NOT caught, here either: unify_step's element MRB always off / always
on (lockstep_unif.py's header).

Not run: a normal link (it needs the boot module, pimos::pim, hence
the system's files); more than one file in a list; a system file
(the reference model stops at new_string with 32-bit elements).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_cons as cons  # noqa: E402
import lockstep_file as lfile  # noqa: E402
import lockstep_gca as gca  # noqa: E402
import lockstep_load as lload  # noqa: E402
import lockstep_modc as modc  # noqa: E402

PINNED = dict(parts=2, lines=8661495)
UNIFIED = 23        # vector pairs the second part's link unifies: three steps each
# (label, the file list)
PARTS = [('load', ['pimm_patch_hash360E.sav']),
         ('six modules', ['pimm_patch_mkdir360E.sav'])]


def unresolved(files):
    """The modules the files call and do not hold, by asm/unlsav.py's
    reading (names as the files spell them: 2 for an underscore)."""
    have, want = set(), []
    for f in files:
        have |= {m['name'] for m in modc.modules(f)}
        for a in gca.areas(f):
            for top in a[3]:
                if top[0] == 'extcall' and top[1][1] not in want:
                    want.append(top[1][1])
    return [w.replace('2', '_') for w in want if w not in have]


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    return s, [one(s, im, names, label, files) for label, files in PARTS]


def one(s, im, names, label, FILES):
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    s.label(label)
    # 0 Files, 1 the open requests, 2 Close, 3 Loaded
    s.setslot(0, (pimm.ATOM, 0))
    for f in reversed(FILES):
        s.string(4, 16, cons.jis(f))
        s.cons(5, 6, ('slot', 4), ('slot', 0))
        s.setslot(0, (0, 0))
        s.newvar(0)
        s.unify(0, 5)
    for i in (1, 2, 3):
        s.newvar(i)
    for a in (1, 2, 3, 4):
        s.arg(a, a - 1)
    s.spawn(pimm.predicate(im, 'ipl_loader', 'load/4'), 4)
    m = s.live()
    opens, streams, todo, asked = s.live_slot[1], [], list(FILES), []
    while True:
        s.run()
        m = s.live()
        progress = False
        w = m.deref(opens)
        if not m.unbound(w) and w[0] & ~1 == pimm.LIST:
            # open(Name, R): R = normal(F), F the stream of getb requests
            req = m.deref((pimm.REF, w[1]))
            asked.append(m.term(req)[:2])
            s.newvar(8)
            s.vector(9, 11, [A('normal'), ('slot', 8)])
            s.setslot(15, (pimm.REF, req[1] + 2))
            s.unify(15, 9)
            m = s.live()
            # a name may be a full path (pimos.ipl's are): the file is its last part
            streams.append([s.live_slot[8], lfile.file_words(todo.pop(0).rsplit('>', 1)[-1])])
            opens = (pimm.REF, w[1] + 1)
            progress = True
        for st in streams:
            while st[1]:
                w = m.deref(st[0])
                if m.unbound(w) or w == (pimm.ATOM, 0):
                    break
                req = m.deref((pimm.REF, w[1]))
                assert m.deref((pimm.REF, req[1])) == A('getb'), req
                chunk, st[1] = st[1][:lload.BUFFER], st[1][lload.BUFFER:]
                s.string(6, 16, chunk)
                s.vector(5, 13, [A('normal'), ('slot', 6)])
                s.setslot(15, (pimm.REF, req[1] + 1))
                s.unify(15, 5)
                st[0] = (pimm.REF, w[1] + 1)
                m = s.live()
                progress = True
        if not progress:
            break
    s.setslot(4, opens)
    for i in (3, 2, 4):
        s.out(i)
    return dict(label=label, files=FILES, asked=asked, left=[len(st[1]) for st in streams],
                todo=todo, waiting=s.live().nsusp)


def check(s, m, wants, parts):
    """parts: {label: trace lines}."""
    bad, shown, named = [], [], []
    for want in wants:
        b, got, name = check_one(s, m, want, parts.get(want['label'], []))
        bad += [(want['label'],) + x for x in b]
        shown.append(got)
        named.append(name)
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    # the six-module file has modules naming the same external module:
    # the linker's get_and_put unifies two vectors (lockstep_unif.py)
    stub = 'I %d ' % m.stubs['$unify_step']['addr']
    steps = [sum(1 for ln in parts.get(w['label'], []) if ln.startswith(stub)) for w in wants]
    if steps[0] != 0 or steps[1] != UNIFIED * 3:
        bad.append(('unify_step taken', steps))
    return bad, shown, named


def check_one(s, m, want, lines):
    bad, FILES = [], want['files']
    loaded, close, opens = [w for l, w in s.outs if l == want['label']][-3:]
    exp_asked = [('open', (16, cons.jis(f))) for f in FILES]
    if want['asked'] != exp_asked or want['todo'] or any(want['left']):
        bad.append(('files asked for', want['asked'], want['left']))
    got = cons.console(lines)
    text = ['IPL loading'] + FILES + ['Link Modules ...']
    if got != text:
        bad.append(('console', got))
    missing = unresolved(FILES)
    # the message and ONE of the missing modules (the linker stops at
    # the first it meets)
    t = None if m.unbound(loaded) else m.term(loaded)
    msg = (8, [ord(c) for c in 'Undefined Module Found'])
    if not (isinstance(t, tuple) and t[0] == 'abnormal' and len(t[1]) == 2 and t[1][0] == msg
            and t[1][1] in [(16, cons.jis(n)) for n in missing]):
        bad.append(('Loaded', str(t)[:200]))
    if not m.unbound(m.deref(opens)):
        bad.append(('the open requests go on', m.term(opens)))
    if want['waiting']:
        bad.append(('%d goals left waiting' % want['waiting'],))
    name = cons.ascii_of(t[1][1][1]) if not bad else None
    return bad, got, name


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        parts = dict(s.play())
        m = s.machine
        print(check(s, m, want, parts), m.hp - m.load, sum(len(v) for v in parts.values()))
        return 0
    kept = {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            yield what, lines
    s.play = keeping
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep link',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, shown, named = check(s, m, want, kept)
    if bad:
        print('pimm lockstep link: FAIL %r' % (bad[:3],))
        return 1
    print("pimm lockstep link: PASS (ipl_loader:load/4, the IPL's loader, atom table and "
          'linker together, on the Bluespec core: %d trace lines identical to the reference '
          'model; a file of one module and a file of six; the console is given %r; the '
          'linker reports an undefined module each time: %r)'
          % (s.counts['lines'], shown[0], named))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
