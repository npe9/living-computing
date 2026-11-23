#!/usr/bin/env python3
"""The long run: the IPL loads and links the whole of pimos.ipl.

    python3 ref/pimm/longrun_ipl.py --script FILE [N]   write the script
    sim_pimm_driver | python3 ref/pimm/longrun_ipl.py compare [N]
    python3 ref/pimm/longrun_ipl.py --reference [N]     reference model alone
    python3 ref/pimm/longrun_ipl.py --reference --go    ... and then PIMOS is entered

Run by bsv/run_pimm_longrun.sh.  NOT part of run_tests.sh.

Checked: every file of the list asked for, in order, and read whole;
Loaded = normal(Atoms, Modules, Comments, Code); Code is a predicate
of arity 4 in the entry table of the module the list has for the atom
pim; every module is the object of the LAST file that holds it, by
its entry table against asm/unlsav.py's reading of that file ("the
last occurrence of that module is valid", PIMOS manual e-sysman.tex):
eight modules are in two files with different tables, and all eight
must be the later one's; no goal left waiting.

Measured 2026-11-23, the reference model alone (--reference): 844 s,
of which 416 s making the script; 1,644,180 script operations;
73,483,342 heap cells; 10,032 atoms, 480 modules, 20 comments.
On BOTH models (bsv/run_pimm_longrun.sh), 2026-11-23: the whole list,
447,739,516 trace lines identical, every check above passing; 7,350 s
on a machine shared with other runs (668 s of it making the script).
That run's simulator was built from the tree of b7187d59.

--go (reference model alone, with what only it has: Machine.ahead):
after the link, top:go_pimos1(Loaded, BootInfo) is started as the IPL
would, apply(Code, {BootInfo, Atoms, Modules, Comments}), and run
until the model refuses something.  It is NOT the IPL's boot: the
goal is started by the bench outside any shoen, BootInfo is an
unbound variable, and no device is attached.  Observed 2026-11-23:
pim:go/4 runs 1,244 instructions in the loaded modules, the console
is given "PIMOS V 3.600 20-May-93" (display_console; the text the
source's default branch gives, bios/boot/bios.kl1 and
kernel/init/version.kl1), and it stops at scsi_where (22:A0, not
implemented).  The check is the banner; the stop is printed, since it
moves as the model grows.

N: only the first N files of the list (for a shorter trial; the link
is then normal only if those files are closed under their calls).
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_cons as cons  # noqa: E402
import lockstep_ipll as ipll  # noqa: E402
import lockstep_link as link  # noqa: E402
import lockstep_modc as modc  # noqa: E402

PINNED = dict(files=20, modules=480, atoms=10032, replaced=8, stay=8, lines=447739516)
T0 = time.time()
BANNER = 'PIMOS V 3.600 20-May-93'


def names():
    """The file names of the held pimos.ipl, as the list spells them."""
    return [cons.ascii_of(line) for line in ipll.by_hand(ipll.list_words())]


def text_of(words):
    """A 16-bit string as text: asm/psdpim.py's table where it has the
    character, else the code in angle brackets."""
    out = ''
    for w in words:
        try:
            out += cons.ascii_of([w])
        except KeyError:
            out += '<%04x>' % w
    return out


def say(text):
    print('%6.0fs %s' % (time.time() - T0, text), file=sys.stderr, flush=True)


def script(files):
    # the trace of the machine the script is made on is not kept
    olive = driver.Script.live

    def live(self):
        m = olive(self)
        m.tr = []
        return m
    driver.Script.live = live
    im = pimm.kbndis.Image()
    atoms = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    want = link.one(s, im, atoms, 'the list', files)
    m = s.live()
    say('script made: %d operations, heap %d cells' % (len(s.ops), m.hp - m.load))
    driver.Script.live = olive
    del s._live                         # that machine's memory is given back
    return s, want


def tables(m, a):
    """The code addresses in the entry table of the module at a, each
    slot and pair walked (lockstep_p2c.public does the same on the
    image)."""
    table = a + 2 + m.mem[a + 1][1]
    out = set()
    for sl in range(table + 1, table + 2 + m.mem[table][1]):
        st, sv = m.mem[sl]
        if st == pimm.INT:
            for k in range(sv >> 16):
                p = sl + (sv & 0xffff) + 2 * k
                out.add(p + 1 + m.mem[p + 1][1])
    return out


def check(s, m, want, files):
    bad = []
    loaded = [w for _l, w in s.outs][-3]
    if want['asked'] != [('open', (16, cons.jis(f))) for f in files] or want['todo'] \
            or any(want['left']):
        bad.append(('files asked for', len(want['asked']), want['left']))
    if m.unbound(loaded) or m.vsize(loaded) != 5:
        return bad + [('Loaded', None if m.unbound(loaded) else str(m.term(loaded))[:300])], {}
    b = m.vbase(loaded)
    el = [m.deref(m.mem[b + i]) for i in range(5)]
    if m.term(el[0]) != 'normal' or el[4][0] != pimm.COD:
        return bad + [('Loaded', el)], {}
    # normal(Atoms, Modules, Comments, Code)
    atoms = m.term(el[1])
    mods = []
    w = el[2]
    while w[0] & ~1 == pimm.LIST:
        r = m.deref(m.mem[w[1]])
        mods.append((m.deref(m.mem[m.vbase(r)]), m.deref(m.mem[m.vbase(r) + 1])))
        w = m.deref(m.mem[w[1] + 1])
    comments = m.term(el[3])
    # the code: a predicate head of arity 4 two cells before it, inside
    # the module the list has for the atom "pim"
    atom_of = {text_of(n[1]): a for n, a in atoms}
    code = el[4][1]
    head = m.mem[code - 2]
    pim = [mo for na, mo in mods if m.term(na) == atom_of.get('pim')]
    if head[0] != pimm.PREDH or head[1] >> 24 != 4 or len(pim) != 1 \
            or code - 2 - (head[1] & 0xffffff) != pim[0][1] or code not in tables(m, pim[0][1]):
        bad.append(('the code is not a predicate of arity 4 of pim', head, pim))
    # a module in two files: the later file's is the one that stays
    # (e-sysman.tex: "the last occurrence of that module is valid")
    last, differs = {}, set()
    for f in files:
        for mo in modc.modules(f.rsplit('>', 1)[-1]):
            locs = frozenset(loc for _n, _a, loc in mo['preds'])
            if mo['name'] in last and last[mo['name']] != locs:
                differs.add(mo['name'])
            last[mo['name']] = locs
    byname = {}
    for na, mo in mods:
        byname.setdefault(m.term(na), []).append(mo)
    stay = 0
    for name, locs in last.items():
        # the file spells an underscore as 2 (its JIS row dropped)
        cands = [a for n, a in atom_of.items() if n.replace('_', '2') == name]
        objs = [mo for a in cands for mo in byname.get(a, [])]
        if len(objs) != 1:
            bad.append(('module %s: %d objects' % (name, len(objs)),))
            continue
        a = objs[0][1]
        if {t - a for t in tables(m, a)} != set(locs):
            bad.append(('module %s is not its last file\'s' % name,))
        elif name in differs:
            stay += 1
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    info = dict(atoms=len(atoms), modules=len(mods), comments=len(comments),
                replaced=len(differs), stay=stay, heap=m.hp - m.load,
                first_comment=(text_of(comments[0][0][1]),
                               ''.join(map(chr, comments[0][1][1])) if comments[0][1] else None)
                if comments else None)
    return bad, info


def main(argv):
    n = int(argv[-1]) if argv[-1].isdigit() else None
    files = names()[:n]
    s, want = script(files)
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        m = pimm.Machine()
        for _what, lines in s.play(m):
            lines.clear()
        ok, counts = True, dict(lines=None)
    else:
        ok, m = driver.compare(s, sys.stdin, 'pimm longrun ipl')
        counts = getattr(s, 'counts', {})
        if not ok:
            return 1
    bad, info = check(s, m, want, files)
    if '--go' in argv and '--reference' in argv and not bad:
        loaded = [w for _l, w in s.outs][-3]
        im = pimm.kbndis.Image()
        m.ahead = True
        m.argv[1], m.argv[2] = pimm.marked(loaded), pimm.marked(m.new_var())
        m.record(pimm.READY, pimm.predicate(im, 'top', 'go_pimos1/2'), m.argv[1:3])
        m.tr = []
        try:
            m.run()
            stop = 'nothing left to run, %d goals waiting' % m.nsusp
        except pimm.Unimplemented as e:
            stop = 'refused: %s' % e
        except (pimm.Suspend, pimm.Fail) as e:
            stop = type(e).__name__
        shown = cons.console(m.tr)
        info['go'] = dict(instructions=sum(1 for ln in m.tr if ln[0] == 'I'), console=shown,
                          stop=stop)
        if shown[:1] != [BANNER]:
            bad.append(('the console after go', shown))
    say('compared')
    whole = n is None
    if bad or (whole and any(info.get(k) != PINNED[k] for k in ('modules', 'atoms', 'replaced', 'stay'))) \
            or (whole and len(files) != PINNED['files']) \
            or (whole and '--reference' not in argv and counts.get('lines') != PINNED['lines']):
        print('pimm longrun ipl: FAIL %r %r %r' % (bad[:4], info, counts))
        return 1
    print('pimm longrun ipl: PASS (ipl_loader:load/4 on %s: %d files loaded and linked, the '
          'answer normal with the code of pim:go/4; %s trace lines identical to the reference '
          'model; %r)' % ('the reference model alone' if '--reference' in argv
                          else 'the Bluespec core', len(files), counts.get('lines'), info))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
