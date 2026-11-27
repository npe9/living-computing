#!/usr/bin/env python3
"""MENDELS (IFS No.61) on PIMOS and SIMPOS together: the KL1 half on
PIMOS (ref/pimm/pimm.py, from the shell's prompt), the ESP half on the
PSI (psi/kl0.py, compiled by psi/espc.py), linked as the real system
linked them, by the FEP's string I/O (fep#create_string_io, 601, and
its io, 620) to an ESP class of the package `mendel`.  OURS.

    python3 -I psi/mendels.py live PROMPT.pkl [--route doc|prompt] [--answer TEXT ...]
                              [--record TAPE] [--png FILE]
        PROMPT.pkl: the machine at the shell's prompt (ref/pimm/
        ifs_sweep.py's header).  The archive's files served as
        readme.e/install.e put them; shell.com1's lines typed.  --route
        doc (default): mendel.pac served in >sys>user>MENDEL>KL1, the
        task directory set there (shell.com1:22-23), so package/2 reads
        the package name from the file; --route prompt: the sweep row's
        lines (no mendel.pac), so package.kl1's read_window asks
        `package>>` and --answer is typed there.
    python3 -I psi/mendels.py replay TAPE [--key LINE ...] [--lenient] [--png FILE]
        the PSI side alone, fed PIMOS's packets from TAPE (the user's
        lines USER_LINES, or each --key; --lenient: PIMOS sends nothing
        once the PSI's packets leave the tape's, for a shorter dialogue's
        frame, e.g. --key '>sys>user>MENDELuser' for the path dialog)
    python3 -I psi/mendels.py compile
        the package's ESP half compiled; the dropped and refused items

The link.  package.kl1's ckcreate_esp_device/2 and main.kl1's
mendel_loader/3 ask PIMOS's string_io device for `create(Name, D)`,
Name "mendel##mendel_esp_device", "mendel##mendel_loader",
"mendel##esp_utility" (package.kl1:105-117, 124-133; main.kl1:24-36):
PIMOS sends the FEP 601 with that name, and the PSI's held
pimfep##pimos_string_io_invoker makes an instance of the class it names
(psi/README.md "The string-I/O recipe").  Each class is an heir of
pimfep##as_pimos_string_io_device (esp_device.esp:7-8, loader.esp:7-8,
esp_util.esp:7-8) and answers io(Code, String) by its :io/4.  The bridge
(psi/fep_bridge.py's, OURS) carries 601 and every later message to such
a device; everything else (the files, the shell's window) stays
ref/pimm/fep.py's, with the sweep runner's services (ifs_sweep.py).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'ref', 'pimm'))
import espc  # noqa: E402
from espc import esplex  # noqa: E402
import fep_bridge as FB  # noqa: E402
import kl0 as K  # noqa: E402
import simpos_fs as FS  # noqa: E402

ARCHIVE = 'exper-apps/pimos/mendels.tar.Z'
T0 = time.time()


def say(text):
    print('%6.0fs %s' % (time.time() - T0, text), file=sys.stderr, flush=True)


# -- the ESP half -------------------------------------------------------------

def esp_sources():
    """{base name: text} of the archive's ESP files (mendels/*.esp and the
    one whose name the tar cut short, main_reduce.es), read in memory"""
    import ifs_sweep as X
    files = X.archive(ARCHIVE)
    out = {}
    for n, raw in sorted(files.items()):
        if n.startswith('mendels/') and (n.endswith('.esp') or n.endswith('.es')):
            out[os.path.basename(n)], _e = esplex.decode(raw)
    return out


def compile_package():
    """The package `mendel` (install.e Step 5-6: every ESP file catalogued
    into it) compiled as one unit.  -> (templates, report): report lists
    every item dropped by the parser and every predicate espc refuses, so
    nothing vanishes silently (espc.compile_text's rule, kept as a report
    here: the held source is not edited)"""
    defs, dropped = [], []
    for name, text in esp_sources().items():
        d, nerr = espc.parse_text(text, name)
        for line in espc.source_refusals(d, name):
            dropped.append('%s: %s' % (name, line))
        if nerr and not any(x.startswith(name) for x in dropped):
            dropped.append('%s: %d items not parsed' % (name, nerr))
        defs += d
    ts, failed = espc.compile_classes(defs, 'mendel')
    refused = [(t.id, k, why, str(detail)) for t in ts for k, why, detail in t.refusals]
    return ts, dict(dropped=dropped, failed={c: str(e) for c, e in failed.items()},
                    refused=refused)


# -- the PIM/m side -------------------------------------------------------------

LINES_DOC = ['package:define(mendel,user) .', 'setenv task:package = mendel .',
             'setenv task:directory = ">sys>user>MENDEL>KL1" .',
             'setenv task:home = ">sys>user>MENDEL>KL1" .',
             'load(">sys>user>MENDEL>mendel.exe") .',
             'relink([mendel,tableau_main,execute_main,mdl_compiler,mendel_package,esp_utility,'
             'graph,decomp,net,scc,prim])', 'mendel .']


def row_for(route, answers=()):
    """the sweep row (ifs_rows.py mendels) for --route prompt, or the
    documented installation for --route doc (readme.e:18-28, install.e:
    'Copied Files'; shell.com1:20-23, 39-44)"""
    import ifs_sweep as X
    row = dict(X.ROWS['mendels'])
    if route == 'doc':
        row['serve'] = [(r'^mendels/mendel\.exe$', '>sys>user>MENDEL>'),
                        (r'^mendels/mendel\.pac$', '>sys>user>MENDEL>KL1>'),
                        (r'^mendels/mdllibrary\.exe$', '>sys>user>MENDELuser>SYSTEM>')]
        row['typed'] = list(LINES_DOC)
    row['typed'] = list(row['typed']) + list(answers)
    return row


class PimSide:
    """PIMOS from the prompt checkpoint; its Fep made a bridge: a device
    made by 601 is the PSI's (fep_bridge.BridgeFep.packet), the rest as
    the sweep runner serves it"""

    def __init__(self, pkl, row, budget=200_000_000):
        import ifs_sweep as X
        import lockstep_shell as ls
        import longrun_ipl as L
        m, loaded, _i, kind = ls.load(pkl)
        assert kind == 'prompt'
        m.ahead = False
        m.heap_limit = X.HEAP_LIMIT
        m.gc_paths = None
        self.served = X.serve(row)
        X.install_listing()
        X.install_write_files(m.fep)
        dev = m.fep
        dev.__class__ = type('MendelsFep', (FB.BridgeFep,), dict(BRIDGED=(601,)))
        dev.bridged, dev.to_psi = set(), []
        dev.open_file = L.kernel_file
        dev.list_dir = L.home_listing
        typed = row['typed']
        dev.script = [('getl', ln) for ln in typed]
        m.tr = X.Capped(budget)
        self.m, self.dev, self.log0 = m, dev, len(dev.log)

    def run(self):
        import pimm
        m, dev = self.m, self.dev
        skips = 0
        while True:
            try:
                m.run(limit=10 ** 12)
            except pimm.Suspend:
                pass
            if m.scsi_poll():
                skips = 0
                continue
            if m.alarm_var is not None:
                skips += 1
                if skips > 100:
                    raise pimm.Unimplemented('100 alarms in a row with nothing else to do')
                m.alarm_skip()
                continue
            skips = 0
            if dev.to_psi:
                break
            if not dev.idle():
                break
            say('pim: a typed line at %d instructions' % m.tr.instructions)
        out, dev.to_psi = dev.to_psi, []
        return out

    def window(self):
        return ''.join(t for _d, t in self.dev.log[self.log0:])


# -- the PSI side -------------------------------------------------------------

# The PSI user pmpsi registered a second time, with the password the
# prompt checkpoint's login gave PIMOS: that login was fep.py's scripted
# one, RP "" (fep.LOGIN), where fep_bridge's own run logs in through the
# PSI with RP "pmpsi" (README step 3n; simpos_fs.mount registers that
# one).  The held pimos_string_io_invoker identifies the 601's user and
# password with the PSI's (as_pimos_device > simpos_user > user
# identify/4; OBSERVED 2026-11-27: with only "pmpsi" registered, 601 is
# answered 5 and get_class_object/3 is never reached).  OURS, as both
# passwords are: no source gives either
CHECKPOINT_PASSWORD = ''


# The PSI's directories that MENDELS's installation makes (install.e
# Step 1, its "Directory Structure"; readme.e:18-28): HELD placement.
# They are made empty (OURS): nothing on the run's path reads a file in
# them yet; the path window checks that the user directory and its four
# subdirectories exist (init_path.esp check_pathname2/3, get_sysDIRs/3)
INSTALLED_DIRS = ['>sys>user>MENDEL', '>sys>user>MENDEL>ESP', '>sys>user>MENDEL>KL1',
                  '>sys>user>MENDELuser', '>sys>user>MENDELuser>PARTS',
                  '>sys>user>MENDELuser>SYSTEM', '>sys>user>MENDELuser>TEMP',
                  '>sys>user>MENDELuser>USER']
# What the user types into the ESP half's windows (OURS: readme.e:37-39
# "please input a parent directory of user files like
# >sys>user>MENDELuser"; then `y` to init_path.esp's "OK?(y/n)>")
USER_LINES = ['>sys>user>MENDELuser', 'y']


# The fonts MENDELS opens that no held file holds (OURS substitution):
# `font:kanji_16.font` (mendel_win.esp create_kanji_font/1, title.esp,
# lib_win.esp, ...) is not in psdpim's FONT.DIR, whose seven fonts have no
# kanji (simpos_fs.py's `font:` placement); its name is entered in
# >sys>font for test_11.font's file, as window M10's exshow test entered
# kanji_28.font (psi/test_espc.py m10_start).  Without it font create/3
# fails (font.esp, INFERENCE) and mendel_window's create_window/1 with it
SUBSTITUTE_FONTS = [('kanji_16.font', 'test_11.font')]


def _entries(m, d):
    t, out = K.deref(m.get_slot(d, 'entries')), []
    while isinstance(t, K.Cons):
        e = K.deref(t.args[0])
        out.append((K.deref(e.args[0]).text, K.deref(e.args[1])))
        t = K.deref(t.args[1])
    return out


def substitute_font(m, name, held_font):
    """NAME entered in >sys>font for HELD_FONT's file (OURS, above)."""
    d = m.get_slot(K.ClassRef('simpos##directory'), 'root')
    for part in FS.FONT.strip('>').split('>'):
        d = dict(_entries(m, d))[part]
    f = dict(_entries(m, d))[held_font]
    m.set_slot(d, 'entries', K.Cons(K.Vec([K.Str(name), f]), m.get_slot(d, 'entries')))


class PsiSide(FB.PsiSide):
    """fep_bridge's PSI side (the boot program, the held front end on two
    streams, the coordinator), no login typed, the package `mendel`
    added to the library"""

    def __init__(self, keys=USER_LINES, max_steps=50_000_000):
        ts, failed = espc.compile_text(FB.BOOT, 'simpos')
        assert not failed
        mts, self.report = compile_package()
        lib = K.load_six()
        for t in espc.standins() + ts + mts:
            lib.add(t)
        m = K.Machine(lib, max_steps=max_steps)
        saved = FS.EMPTY_DIRS
        FS.EMPTY_DIRS = list(saved) + INSTALLED_DIRS
        try:
            FS.mount(m)
        finally:
            FS.EMPTY_DIRS = saved
        for name, held_font in SUBSTITUTE_FONTS:
            substitute_font(m, name, held_font)
        m.reset()
        U = K.ClassRef('simpos##user')
        for _ in m.solve_send(U, 'register', [K.Str(FS.USER), K.Str(CHECKPOINT_PASSWORD),
                                              K.Atom('general'), U]):
            break
        (prog,) = K.call_class_method(m, 'simpos##b3n_boot', 'create', [K.Var()])[0]
        (fi,) = K.call_class_method(m, 'simpos##stream', 'create', [K.Var()])
        (fo,) = K.call_class_method(m, 'simpos##stream', 'create', [K.Var()])
        self.fe_in, self.fe_out = fi[0], fo[0]
        m.set_slot(prog, 'fe_in', self.fe_in)
        m.set_slot(prog, 'fe_out', self.fe_out)
        self.script = dict(login=FB.key_script(*keys), shell=[])
        self.user = [FB.event(j) for j in self.script['login']]
        self.shell = [FB.event(j) for j in self.script['shell']]
        self.user_at = self.shell_at = None
        self.windows, self.getl, self.exchanges = set(), False, 0
        self.m, self.prog = m, prog


def live(pkl, route='doc', answers=(), record=None):
    pim = PimSide(pkl, row_for(route, answers))
    psi = PsiSide()
    tape = []

    def exchange(from_psi):
        for raw in from_psi:
            say('psi > pim %r' % (FB.show(raw),))
            pim.dev.from_psi(raw)
        to_psi = pim.run()
        for raw in to_psi:
            say('pim > psi %r' % (FB.show(raw),))
        tape.append(dict(from_psi=[r.hex() for r in from_psi], to_psi=[r.hex() for r in to_psi]))
        return to_psi
    try:
        stop = psi.run(exchange)
        stop = '%s: %s' % (stop.cause, stop.detail) if stop else None
    except Exception as e:      # the PIM/m side's stop (a FepError, the budget)
        stop = '%s: %s' % (type(e).__name__, e)
    result = dict(route=route, answers=list(answers), stop=stop, where=psi.where(),
                  window=pim.window()[-4000:], instructions=pim.m.tr.instructions,
                  exchanges=len(tape), screen=FB.screen(psi))
    if record:
        with open(record, 'w') as f:
            json.dump(dict(route=route, answers=list(answers), exchanges=tape, result=result),
                      f, indent=1)
    return result, psi, pim


def replay(path, tape=None, keys=USER_LINES, lenient=False):
    """the PSI side alone, fed the tape's packets from PIMOS; each packet
    the PSI sends checked against the live run's.  KEYS: the user's lines
    (the tape's run typed USER_LINES).  LENIENT: where the PSI's packets
    differ from the tape's, or the tape has no more, PIMOS is taken to
    send nothing (for a screen of a shorter dialogue, KEYS a prefix of the
    tape's); the run then ends as the PSI waits.  -> (stop, psi, left)"""
    if tape is None:
        with open(path) as f:
            tape = json.load(f)
    psi = PsiSide(keys=keys)
    left = list(tape['exchanges'])
    psi.diverged = None
    if os.environ.get('MENDELS_TRACE'):
        trail = psi.trail = []

        def tr(code, c):
            cid = getattr(code, 'id', code)
            if not trail or trail[-1] != cid:
                trail.append(cid)
                del trail[:-400]
        psi.m.trace = tr

    def exchange(from_psi):
        if lenient and (psi.diverged is not None or not left
                        or [r.hex() for r in from_psi] != left[0]['from_psi']):
            if psi.diverged is None:
                psi.diverged = psi.exchanges
            return []
        if not left:
            raise AssertionError('the PSI asks for an exchange the tape does not have')
        e = left.pop(0)
        got = [r.hex() for r in from_psi]
        if got != e['from_psi']:
            raise AssertionError('the PSI sent %r, the live run %r'
                                 % ([FB.show(r) for r in from_psi],
                                    [FB.show(bytes.fromhex(r)) for r in e['from_psi']]))
        return [bytes.fromhex(r) for r in e['to_psi']]
    stop = psi.run(exchange)
    return stop, psi, left


def strings_io(tape):
    """The string-I/O messages of a tape, in order: ('>', dev, code, text)
    for PIMOS's io (620) to an ESP device, ('<', dev, status, text) for the
    PSI's answer to it; 601 creates as ('create', dev, name) and closes as
    ('close', dev)"""
    out, ios = [], set()
    for e in tape['exchanges']:
        for h in e['to_psi']:
            p = FB.show(bytes.fromhex(h))
            if p[2] == 601:
                out.append(('create', p[0], FB.fepm.unjis(p[6])))
            elif p[2] == 620:
                ios.add(p[0])
                out.append(('>', p[0], p[3], FB.fepm.unjis(p[4])))
            elif p[2] == 60:
                out.append(('close', p[0]))
        for h in e['from_psi']:
            p = FB.show(bytes.fromhex(h))
            if p[0] in ios and len(p) > 3:
                out.append(('<', p[0], p[2], FB.fepm.unjis(p[3]) if isinstance(p[3], bytes) else p[3]))
    return out


def png(psi, path):
    import windev
    with open(path, 'wb') as f:
        f.write(windev.png_bytes(windev.device(psi.m).frame))


def main(argv):
    if len(argv) > 2 and argv[1] == 'replay':
        keys = [argv[i + 1] for i, a in enumerate(argv) if a == '--key'] or USER_LINES
        stop, psi, left = replay(argv[2], keys=keys, lenient='--lenient' in argv)
        if '--png' in argv:
            png(psi, argv[argv.index('--png') + 1])
        print('stop: %s: %s' % (stop.cause, stop.detail) if stop else 'stop: none')
        print('where: %r' % (psi.where(),))
        print('exchanges left: %d' % len(left))
        if getattr(psi, 'trail', None):
            print('trail: ' + ' > '.join(map(str, psi.trail[-150:])))
        return 0
    if len(argv) > 2 and argv[1] == 'live':
        route = argv[argv.index('--route') + 1] if '--route' in argv else 'doc'
        answers = [argv[i + 1] for i, a in enumerate(argv) if a == '--answer']
        rec = argv[argv.index('--record') + 1] if '--record' in argv else None
        result, psi, _pim = live(argv[2], route, answers, rec)
        for k, v in result.items():
            print('%s: %r' % (k, v))
        if '--png' in argv:
            png(psi, argv[argv.index('--png') + 1])
        return 0
    if len(argv) > 1 and argv[1] == 'compile':
        ts, rep = compile_package()
        print('classes compiled: %d; failed: %d' % (len(ts), len(rep['failed'])))
        print('items dropped by the parser: %d' % len(rep['dropped']))
        for d in rep['dropped']:
            print('  ' + d[:200])
        print('predicates refused: %d' % len(rep['refused']))
        if '-v' in argv:
            for r in rep['refused']:
                print('  %s %s/%d: %s (%s)' % (r[0], r[1][0], r[1][1], r[2], r[3][:100]))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
