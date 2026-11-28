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
# They are made empty (OURS), but for the held files HELD_FILES places in
# SYSTEM (below); the path window checks that the user directory and its four
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


# The archive's user-defined files, placed as install.e's "Copied Files"
# says (HELD placement, install.e Step 2: "example*.kl1, *.med, *.mdl,
# *.save ( DIR PARTS )", "tree.* ( DIR SYSTEM )"); the MENDEL user
# directory is the one USER_LINES types.  Their text is HELD (the
# archive's bytes, ASCII, newline 0x0a), made 16-bit JIS words as the
# PSI's text files are (simpos_fs.codes_of; OURS: the archive is a Unix
# copy, so the PSI's own words are not held).  object_lib restore/1
# reads tree.obj and tree.key at start-up (object_lib.esp:29-31, 321-325;
# obj_tree.esp:1011-1020: example1-3 are its library's objects).  The
# archive has no tree.field, so field_tree restore/2 takes its "file not
# exist" clause (field_tree.esp:446-447): HELD absence, not ours
USER_DIR = '>sys>user>MENDELuser'
# Only tree.* is placed so far: nothing on the run's path reads PARTS
# yet, and the example files' text is not checked to be plain ASCII.
HELD_FILES = [('mendels/tree.obj', 'SYSTEM'), ('mendels/tree.key', 'SYSTEM')]


def text_codes(raw):
    """The 16-bit JIS words of ASCII text RAW (espc.jis_code; 0x000a a
    newline, as simpos_fs.codes_of measured on login.com)."""
    return [0x0a if ch == '\n' else espc.jis_code(ch) for ch in raw.decode('ascii')]


def install_held_files(m):
    """HELD_FILES entered in the MENDEL user directory (above)."""
    import ifs_sweep as X
    files = X.archive(ARCHIVE)
    root = m.get_slot(K.ClassRef('simpos##directory'), 'root')
    for name, sub in HELD_FILES:
        d = root
        for part in (USER_DIR + '>' + sub).strip('>').split('>'):
            d = dict(_entries(m, d))[part]
        base = name.rsplit('/', 1)[1]
        raw = files[name]
        f = K.make_instance(m, 'simpos##binary_file')
        m.set_slot(f, 'name', K.Str(base))
        m.set_slot(f, 'version', 1)
        m.set_slot(f, 'size', len(raw))
        m.set_slot(f, 'full_name', K.Str('%s>%s>%s.1' % (USER_DIR, sub, base)))
        m.set_slot(f, 'directory', d)
        s = K.Str('')
        s.set_codes(text_codes(raw))
        m.set_slot(f, 'contents', s)
        m.set_slot(d, 'entries', K.Cons(K.Vec([K.Str(base), f]), m.get_slot(d, 'entries')))


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
        install_held_files(m)
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
        if PHASE_WATCH:
            watch_phase(m)
        self.adapted = []

    def run(self, exchange):
        """fep_bridge's run, PIMOS's packets passed through
        adapt_load_answer (below) on their way into the PSI: the tape
        keeps what PIMOS sent"""
        def adapted(from_psi):
            out = []
            for raw in exchange(from_psi):
                new = adapt_load_answer(raw) if LOAD_ADAPTER else raw
                if new != raw:
                    self.adapted.append((raw, new))
                out.append(new)
            return out
        return super().run(adapted)


# The load answer adapted (OURS adapter, 2026-11-28).  The KL1 half's
# call_KL1/2 for load_library passes load:do/4's Status on as it is
# (main.kl1:140-144: `Message = loaded_library(Result)`), while for
# compile1 and save_library it reduces normal(X) to a bare `normal` itself
# (main.kl1:116-120, 135-139).  The ESP half's phase/2 has clauses for
# loaded_library(normal) and loaded_library(abnormal) only
# (mendelmain.esp:382-389).  The PIMOS manual (V3.0, November 1991,
# pimosman Eman/e-proginfo.tex:494-497, PRINTED) says of load:do/4: "The
# atom normal will be returned in the argument Status if the loading
# completes normally, and the atom abnormal will be returned otherwise"
# (unload:do/5 beside it, :504-507, "normal(FullPathName)"), and install.e
# :22-24 names PIMOS 3.0 as MENDELS's OS.  The PIMOS this repository runs
# (pimosobj's 3.6 objects; the held 4.0 source, src/library/loader/
# modtbl.kl1:274-277 check_flush) answers normal(Loaded), the module list:
# OBSERVED here, `loaded_library(normal([mendel:: example1,...]))`.  No
# held source reduces it (searched: every `:- module load` and every
# caller of load:do in pimos.tar.Z and the 348 IFS/ICOT archives, the only
# other being strtgysh's unrelated vload.kl1; MENDELS's KL1 and ESP
# halves; the V3.0 English manual read; man15.ps and man30.j.ps, IFS
# manuals/pimos, searched as PostScript strings only, no load:do/4 entry
# found).  So it is a version mismatch between MENDELS (written to the
# V3.0 manual) and the loader we run; that PIMOS 3.0's loader itself
# answered a bare `normal` is INFERENCE (its code is not held).  The
# adapter puts in the PSI, in place of exactly that string, the string
# MENDELS's own held no-file branch makes PIMOS send (mdl_comp.kl1:43-54,
# `Result = normal`; OBSERVED byte for byte 2026-11-28 by a live run with
# no mdllibrary.exe: io(0, "loaded_library(normal)")).  Any other
# loaded_library(...) string is refused loudly.  The tape keeps PIMOS's
# own string (the adapter runs after the exchange)
LOAD_ADAPTER = True
LOAD_ANSWER = 'loaded_library(normal)'


def adapt_load_answer(raw):
    """RAW, a packet from PIMOS; an io (620) whose string is
    loaded_library(normal([Package:: Module, ...])) -> the same io with
    LOAD_ANSWER; any other loaded_library string but LOAD_ANSWER and
    loaded_library(abnormal) refused; every other packet as it is"""
    import re
    import struct
    p = FB.show(raw)
    if p[2] != 620 or not isinstance(p[4], bytes):
        return raw
    text = FB.fepm.unjis(p[4])
    if not text.startswith('loaded_library('):
        return raw
    if text in (LOAD_ANSWER, 'loaded_library(abnormal)'):
        return raw
    if not re.fullmatch(r'loaded_library\(normal\(\[(\w+:: \w+)(,\w+:: \w+)*\]\)\)', text):
        raise K.Refusal('mendels', 'load answer not adapted: %r' % text)
    return struct.pack('>ii', p[0], p[1]) + FB.fepm.pack_message([620, p[3], FB.fepm.jis(LOAD_ANSWER)])


# The held phase/2 failing (OURS watch, 2026-11-27).  mendel_main's exec/3
# runs `phase(Class, Current_phase)` (mendelmain.esp:242-248) on the phase
# get_phase/2 read back; phase/2's clauses (mendelmain.esp:379-568) cover
# loaded_library(normal) and loaded_library(abnormal) only (`phase(Class,_)`
# at :569 is the last body goal of the compiled1 clause above it: :568 ends
# in a comma), and the held PIMOS 4.0 load:do answers normal(Modules)
# (pimos src/library/unloader/load.kl1:57 check_status(normal(_), ...);
# MENDELS's own no-file branch, mdl_comp.kl1:43-54, answers the bare
# `normal`), so loaded_library(normal([mendel::example1, ...])) matches no
# clause.  exec/3, esp_go/3 and esp_control/2 then fail, and call_esp/3's
# `repeat` (esp_device.esp:31-42) retries with Inst!message unchanged: the
# whole of create/1 and resume/0 runs again (OBSERVED 2026-11-27 before
# this watch: create_window/1's re-entry clause, mendel_win.esp:110-148).
# That retry backtracks over everything create/1 and resume/0 bound, and
# the stand-ins keep pure data in slots (menu items, text rows), which the
# ESP manual forbids ("The slot can contain only atomic data and inpure
# data. Pure data has its value released by backtracking", program-e.tex
# :1899, PRINTED): their items come back unbound (OBSERVED: every menu of
# the zone) and the second pass is not evidence about MENDELS.  So the run
# stops where phase/2 fails, before anything is undone.  The watch fires
# whenever phase/2 fails as a whole; its text says "has no clause for"
# because that is this run's case (phase/2's heads read, mendelmain.esp:
# 379-568): a failure in the last clause's body would be worded the same.
PHASE_WATCH = True


def watch_phase(m):
    """m.fail wrapped: phase/2 of mendel##mendel_main failing as a whole
    (the failure leaves it: the choice point taken is not one of its
    clauses) is a refusal, raised before the unwind (OURS)."""
    import bisect
    orig, keys = m.fail, {}

    def pred(pc):
        code = pc[0] if pc else None
        if not hasattr(code, 'preds'):
            return None, None
        ks = keys.get(code.id)
        if ks is None:
            ks = keys[code.id] = sorted(code.preds)
        i = bisect.bisect_right(ks, pc[1]) - 1
        return code.id, (code.preds[ks[i]].name if i >= 0 else None)

    def fail():
        here = pred(m.pc)
        if here == ('mendel##mendel_main', 'phase'):
            alt = pred(m.stack[-1].alt) if m.stack else (None, None)
            if alt != here:
                raise K.Refusal('mendels', 'held mendel##mendel_main phase/2 has no clause for %s '
                                '(call_esp/3 would retry the same message)' % (K.resolve(m.x[1]),))
        orig()
    m.fail = fail


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
