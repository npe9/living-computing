#!/usr/bin/env python3
"""The IFS sweep (2026-11-26; pimos_roadmap.md section 7, after R9):
every held ICOT Free Software application written for PIMOS, tried on
the reference model as its documentation says, and sorted by outcome.
The table and the stop histogram are docs/ifs_apps.md.

    python3 -I ref/pimm/ifs_sweep.py --list
        every row: the archive, the catalogue number, how it is tried
    python3 -I ref/pimm/ifs_sweep.py --run PROMPT.pkl DIR [--jobs N] [--budget N] [NAME ...]
        each run row (default: all), from the shell's prompt, in a forked
        process of its own: its files served as home files, its lines
        typed; the result in DIR/NAME.json; then --report.  --budget
        overrides the rows' budgets (the long runner: aya+alt, 1.2G)
    python3 -I ref/pimm/ifs_sweep.py --report [DIR]
        each row classified (CLASSIFY below) and checked against PINNED
        (ifs_rows.py); the outcome counts and the stop histograms (first
        stops; second stops, from the +alt rows).  DIR, or the committed
        summary docs/ifs_sweep_results.json.  Ends `ifs sweep: PASS` or
        `ifs sweep: FAIL` and the rows that differ
    python3 -I ref/pimm/ifs_sweep.py --summary DIR
        writes docs/ifs_sweep_results.json from a run (each row's stop,
        counts, !ERROR! lines and the window's end), refused if it would
        classify a row otherwise than the whole window does
    python3 -I ref/pimm/ifs_sweep.py --summary --update DIR
        the same for a partial rerun: the committed summary, the rows run
        in DIR replaced
    python3 -I ref/pimm/ifs_sweep.py --check
        IN run_tests.sh, no checkpoint needed, a few seconds: every
        printed value found in the archive file it is cited from, the
        committed summary against PINNED, and the discriminating
        injections (injections() below) each reported as predicted.
        Ends `ifs sweep check: PASS (N rows)`
    python3 -I ref/pimm/ifs_sweep.py --markdown [DIR]
        the outcome table of docs/ifs_apps.md, the objects' loads and the
        ranking of the stops (ranking() below)

A DOCUMENTED LONG RUNNER, NOT part of run_tests.sh: PROMPT.pkl is the
machine saved at the shell's prompt (lockstep_shell.py's header:
longrun_ipl.py --load LINK --go --fep --save-prompt), ~1.1 GB, not in
git; the whole sweep took 2,504 s ten at a time (2026-11-26), 2,159 s in the rerun of 2026-11-27 (docs/ifs_apps.md 7).  Reference model only (ref/pimm/pimm.py); no row is in lockstep
on the core (the bsv lockstep's rows are lockstep_shell.APPS, R8 and R9).

The route is R8's and R9's (lockstep_shell.play from the prompt, as
r9_mgtp_probe.py and mp1_rebuild.py): the application's files are home
files (longrun_ipl.add_home_file for text, HOME>NAME; an object file is
served byte for byte, as the held pimos: set is), read at run time from
the archive under docs/nonlocal/ifs (committed, IFS_MANIFEST.md), never
from an extraction; then the documentation's own lines are typed at the
shell or the Listener.  Sources are served as distributed: no row edits
a file (unlike R8's NAME_r8.kl1); two serve one under a second name as
well (aya+alt's ayaparse.k1l as .kl1, cohlex's Makefile. as Makefile,
each OURS in ifs_rows.py); a refusal of the distributed text is the
recorded stop.  Files are served where the documentation puts them:
flat in HOME, as a tree below it (HOME>prog>compile>X) or in an absolute
directory it names (serve(), install_listing()); text in 7-bit JIS is
served as EUC (jis_to_euc).  What the runner adds, each OURS and in
docs/ifs_apps.md 1: the package work typed first (WORK), R7G's collector
with a 50M-cell limit (run_row), FEP services fep.py lacks
(install_write_files; since 2026-11-27 also the root and the
directories on the way, 237 with any wildcard, versioned opens, "..",
221 on a written file: install_listing, checked by services_check), and for a Listener take the file's commands typed
one by one (expand_take, the +alt rows).  Downloads are untrusted: nothing in
them is executed on the host; they are data given to the model.

Each run has a BUDGET of instructions (not seconds, so the outcome does
not depend on the host's load).  A run that spends it is BUDGET, never
a stop or a success.

CLASSIFY (the outcome of a run row, from its window and its stop):
  memory          `heap full` / `gc: the to-space is full`: STOPS(memory)
  model stop      `refused: ...` from pimm.py (an instruction, built-in
                  or feature the model lacks): STOPS(model: WHAT), and
                  STOPS(float) when WHAT is a floating-point operation
  compiler        the held 3.6 compiler's first `!ERROR!` (a construct
                  of PIMOS 3.0-3.5 it rejects, a missing macro library):
                  STOPS(compile: TEXT)
  dependency      `undefined module` / `non existent module` / a file the
                  FEP does not have: STOPS(missing: WHAT)
  fep             `FepError` from fep.py, the FEP stand-in (a service it
                  does not give): STOPS(fep: WHAT)
  budget          BUDGET (the cap was spent first, with no error before)
A model stop or a FEP error ends the run and is the first stop even when
the window shows an !ERROR! before it (the errors are listed beside it
in the summary): it is what would block the application with its own
errors mended.  An error in the window is the stop when the run went on
to spend its budget.
  else            RUNS-MATCHES when every printed value of the row is in
                  the window (the row says which values), RUNS-DIFFERS when
                  one is not, RUNS-NO-ORACLE when the row has none
A row whose application needs SIMPOS (an ESP half the KL1 reaches
through a string_io device of an ESP class) is NEEDS-SIMPOS whatever its
KL1 half did; the KL1 half's first stop is reported beside it.  When a
float stop and a SIMPOS need both apply, NEEDS-SIMPOS wins the outcome
and the float stop is the first stop (the histogram counts the first
stop).  NEEDS-OTHER: the application needs a host the model has no
stand-in for (UNIX client over a socket, KLIC, a Prolog step on UNIX),
or its files are damaged or missing; those with nothing to run are
static rows, not run (editalign and mssd run their KL1 half).

Measured speed: 26,598,077 instructions in about 235 s (mgtp_q6 from
the prompt, 2026-11-26, at a load average over 200); the PIMOS compiler
on the model, about 50,000 instructions a source line.
"""
import io
import json
import os
import re
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fep as fepm  # noqa: E402
import lockstep_shell as ls  # noqa: E402
import longrun_ipl as L  # noqa: E402

IFS = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'ifs')
HEAP_LIMIT = 50_000_000   # cells; why this size: run_row

_tars = {}


def archive(path):
    """{member name: bytes} of the archive IFS/PATH (compress or gzip)"""
    if path not in _tars:
        full = os.path.join(IFS, path)
        if path.endswith('.Z'):
            raw = subprocess.run(['uncompress', '-c', full], capture_output=True,
                                 check=True).stdout
            t = tarfile.open(fileobj=io.BytesIO(raw))
        else:
            t = tarfile.open(full)
        files = {}
        for e in t.getmembers():
            if e.isfile():
                files[e.name.lstrip('./')] = t.extractfile(e).read()
        _tars[path] = files
    return _tars[path]


def serve_binary(name, raw):
    """HOME>NAME served byte for byte (an object file: the held pimos:
    set is served so, longrun_ipl.held_object), with 221 and 222 answered
    as for a text home file"""
    L.HOME_FILES[name] = (('bytes',), None, None, None, None)
    L._home[name] = fepm.FileData(
        raw, 'PSI::%s>%s.1' % (L.HOME, name),
        fepm.attribute_string('pmpsi', 'pmpsi', '20-May-93', '00:00:00', '20-May-93',
                              '00:00:00', 1, len(raw), 0))


_abs = {}


def serve_abs(path, raw):
    """PATH (">sys>user>DIR>NAME", outside HOME) served from now on, in
    this process only: longrun_ipl.kernel_file answers None (abnormal)
    for any >sys>user> name but HOME's, so it is wrapped here (OURS; the
    wrapper is installed once, by the first such file)"""
    if not _abs:
        orig = L.kernel_file

        def kernel_file(p):
            name = L.text_of(__import__('struct').unpack('>%dH' % (len(p) // 2), p))
            if name in _abs:
                return _abs[name]
            return orig(p)
        L.kernel_file = kernel_file
    data = raw if is_object(raw) else L.home_bytes(jis_to_euc(raw))
    _abs[path] = fepm.FileData(
        data, 'PSI::%s.1' % path,
        fepm.attribute_string('pmpsi', 'pmpsi', '20-May-93', '00:00:00', '20-May-93',
                              '00:00:00', 1, len(data), 0))


def served_dirs():
    """every directory that holds a served file, and each of its
    ancestors up to the root ">": HOME, HOME's subdirectories (the
    trees), serve_abs's directories"""
    dirs = set()
    for n in L.HOME_FILES:
        parts = n.split('>')[:-1]
        for k in range(len(parts) + 1):
            dirs.add('>'.join([L.HOME] + parts[:k]))
    for a in _abs:
        dirs.add(a[:a.rindex('>')])
    out = set()
    for d in dirs:
        parts = d.split('>')
        for k in range(1, len(parts) + 1):
            out.add('>'.join(parts[:k]) or '>')
    return out


def install_listing():
    """a directory below HOME (HOME>DIR, served from a tree) or one of
    serve_abs's listed as HOME is (longrun_ipl.home_listing answers only
    for HOME): the names served directly in it, ".1" each (OURS, for
    the wildcards of the applications' command files, compile"Bel>*.kl1").
    Since 2026-11-27 (cohlex, dulcinea): also the root ">" and every
    directory on the way to a served one (">sys", ">sys>user"), and each
    directory lists the directories in it, by name with no version
    (fep.listing's header: no period, a directory, shell/utils/
    pathname.kl1 is_directory_or_file/4).  The shell expands a wildcard
    of an absolute path from the root: expandPathname's
    checkPathnameList(absolute, ..) opens `directory(">",
    normal(Dir,_,_))` and asks `listing("sys", S)` of it, then of each
    directory down the path (pathname.kl1 183-189, checkNode 254-271),
    and a directory the FEP refuses fails that unification (cohlex's
    `compile(["*.mac"])`, OBSERVED 2026-11-27: 204 on ">" answered 5,
    then `a goal failed inside a shoen` in fileRfil's
    -directory$$$enu$1/4).  A PSI's FEP has the root; what it lists
    there is INFERENCE (the directories on the way only).  OURS, the
    runner's only"""
    orig = L.home_listing

    def home_listing(path):
        name = L.text_of(__import__('struct').unpack('>%dH' % (len(path) // 2), path))
        pre = name if name == '>' else name + '>'
        dirs = served_dirs()
        if name not in dirs:
            return orig(path)
        if name == L.HOME and not any('>' in n for n in L.HOME_FILES):
            return orig(path)
        sub = sorted({d[len(pre):] for d in dirs if d.startswith(pre) and d != name
                      and '>' not in d[len(pre):]})
        if name == L.HOME or name.startswith(L.HOME + '>'):
            rel = '' if name == L.HOME else name[len(L.HOME) + 1:] + '>'
            names = [n[len(rel):] for n in L.HOME_FILES if n.startswith(rel)]
        else:
            names = [n[len(pre):] for n in _abs if n.startswith(pre)]
        names = sorted(n for n in names if '>' not in n)
        return fepm.listing(sub + [n + '.1' for n in names])
    L.home_listing = home_listing

    # A served file opened by its listed name, the version on (the
    # shell's wildcard expansion gives the compiler
    # ">sys>user>pmpsi>cohlex>layout1.mac.1", `!ERROR! unable to open
    # file` for each before this, OBSERVED 2026-11-27): the file of that
    # name without ".1", the one version served (OURS; a FEP's file
    # system keeps versions, INFERENCE that it opens one named so)
    korig = L.kernel_file

    def kernel_file(p):
        name = L.text_of(__import__('struct').unpack('>%dH' % (len(p) // 2), p))
        if name.endswith('.1') and name.count('.') >= 2 and '>' in name:
            got = korig(fepm.jis(name[:-2]))
            if got is not None:
                return got
        return korig(p)
    L.kernel_file = kernel_file


def resolve_parent(path):
    """a directory path with its ".." nodes resolved (">a>b>.." is
    ">a"); the path unchanged if it has none"""
    if '>..' not in path:
        return path
    out = []
    for node in path.split('>')[1:]:
        if node == '..':
            if out:
                out.pop()
        else:
            out.append(node)
    return '>' + '>'.join(out)


def wildcard_match(pattern, entry):
    """237 with a wildcard other than fep.py's "*.*" (the shell's
    listing("sys", S), listing("*.mac", S): pathname.kl1 checkNode):
    `*` any characters, `?` one (INFERENCE: fnmatch's); a pattern of no
    more than one period is matched against the entry without its
    version (meta.mac.1 as meta.mac; a directory as its name), a longer
    one against the whole entry.  OURS"""
    import fnmatch
    if pattern.count('.') < 2 and entry.count('.') >= 2:
        entry = entry[:entry.rindex('.')]
    return fnmatch.fnmatchcase(entry, pattern)


def jis_to_euc(raw):
    """a 7-bit JIS (ISO-2022-JP) text as EUC, the code longrun_ipl.home_bytes
    reads: the bytes between ESC $ B (or ESC $ @) and ESC ( B / ESC ( J
    with their high bit set, the escapes dropped.  Several archives keep
    their text in JIS (rodin's INSTALL:61,101 asks for the conversion to
    PSI code when the files are moved to the FEP; OURS, the same step)"""
    if b'\x1b$' not in raw:
        return raw
    out, kanji, i = bytearray(), False, 0
    while i < len(raw):
        if raw[i] == 0x1b and raw[i + 1:i + 3] in (b'$B', b'$@'):
            kanji, i = True, i + 3
            continue
        if raw[i] == 0x1b and raw[i + 1:i + 3] in (b'(B', b'(J'):
            kanji, i = False, i + 3
            continue
        c = raw[i]
        out.append(c | 0x80 if kanji and 0x21 <= c <= 0x7e else c)
        i += 1
    return bytes(out)


def is_object(raw):
    """a PIMOS object file: magic 5502h, 5602h or 5702h"""
    return raw[:2] in (b'\x55\x02', b'\x56\x02', b'\x57\x02')


TEXTS = {}  # home name -> the text served (EUC bytes), for {TAKE ...}


def commands(text):
    """a Listener command file's commands, in order: each term up to a
    '.' followed by white space (or the end), `%` comments dropped,
    white space runs made one blank; quotes respected"""
    out, cur, q, i = [], [], None, 0
    while i < len(text):
        c = text[i]
        if q:
            cur.append(c)
            if c == q:
                q = None
        elif c in '"\'':
            q = c
            cur.append(c)
        elif c == '%':
            while i < len(text) and text[i] != '\n':
                i += 1
            continue
        elif c == '.' and (i + 1 == len(text) or text[i + 1].isspace()):
            cmd = ' '.join(''.join(cur).split())
            if cmd:
                out.append(cmd + '.')
            cur = []
        else:
            cur.append(c)
        i += 1
    cmd = ' '.join(''.join(cur).split())
    if cmd:
        # the last command without its '.' (a shell file, colodex's
        # s.com, examds's cmpMDL5gc.inf): the Listener needs one
        out.append(cmd + '.')
    return out


def split_top(cmd, sep):
    """cmd split at sep outside quotes and brackets, parts stripped"""
    out, cur, depth, q = [], [], 0, None
    for c in cmd:
        if q:
            q = None if c == q else q
        elif c in '"\'':
            q = c
        elif c in '([{':
            depth += 1
        elif c in ')]}':
            depth -= 1
        elif c == sep and depth == 0:
            out.append(''.join(cur).strip())
            cur = []
            continue
        cur.append(c)
    out.append(''.join(cur).strip())
    return [p for p in out if p]


TAKE = re.compile(r'^take\s*\(?\s*"?([^"()]+?)"?\s*\)?\s*\.$')


CD = re.compile(r'^cd\s*\(?\s*"([^">]*(?:>[^">]*)*)"\s*\)?\s*\.$')


def expand_take(name, depth=0, cwd=None):
    """{TAKE NAME} in a row's typed lines: the command file's commands
    typed one by one, a take inside it expanded the same way (OURS: what
    the Listener's take would read; the take itself stops at
    set_constant, OBSERVED 2026-11-26).  A relative cd in the file is
    typed and followed for the takes after it (dulcinea's install.com:
    cd"rosi", take"Compile", cd"..").  A file not served stays a take"""
    cwd = [] if cwd is None else cwd
    here = '>'.join(cwd + [name]) if cwd else name
    for n in (here, here + '.com'):
        if n in TEXTS and depth < 8:
            out = []
            for cmd in commands(TEXTS[n].decode('euc-jp', 'replace')):
                # a take in a sequence (`take"Compile" ; dfp(soc2).`,
                # dulcinea's install.com:11): the parts typed one by one
                parts = split_top(cmd[:-1], ';') if 'take' in cmd else [cmd[:-1]]
                for part in parts:
                    t, c = TAKE.match(part + '.'), CD.match(part + '.')
                    if c and not c.group(1).startswith('>'):
                        for d in c.group(1).split('>'):
                            if d == '..':
                                cwd[-1:] = []
                            elif d:
                                cwd.append(d)
                    out += expand_take(t.group(1), depth + 1, cwd) if t else [part + '.']
            return out
    return ['take("%s").' % name]


def serve(row):
    """the row's files as home files; returns the names served"""
    served = []
    for ent in row.get('serve', ()):
        pat, rename = ent[0], ent[1]
        files = archive(ent[2] if len(ent) > 2 else row['archive'])
        rx = re.compile(pat)
        hits = sorted(n for n in files if rx.search(n))
        assert hits, '%s: nothing in %s matches %r' % (row['name'], row['archive'], pat)
        for n in hits:
            # rename: None serves the file flat (its base name); a string
            # ending in '/' is a root, the path below it served with '>'
            # (HOME>DIR>NAME, as the documentation's relative paths name
            # it; fep.py's kernel_file passes it to home_file whole)
            raw = files[n]
            if rename and rename.startswith('>'):
                # an absolute directory the documentation installs into
                # (">sys>user>cgs>"): the file served flat there
                serve_abs(rename + os.path.basename(n), raw)
                served.append(rename + os.path.basename(n))
                continue
            if rename and rename.endswith('/'):
                root = '' if rename == '/' else rename
                assert n.startswith(root), (n, rename)
                home = n[len(root):].replace('/', '>')
            else:
                home = rename if rename else os.path.basename(n)
            if is_object(raw):
                serve_binary(home, raw)
            else:
                L.add_home_file(home, jis_to_euc(raw))
                TEXTS[home] = jis_to_euc(raw)
            served.append(home)
    return served


class Budget(Exception):
    pass


class Capped(ls.Sink):
    """the trace to nowhere, the instructions counted, stopped at cap"""

    def __init__(self, cap):
        ls.Sink.__init__(self, None)
        self.cap = cap

    def append(self, line):
        self.lines += 1
        if line[0] == 'I':
            self.instructions += 1
            if self.instructions > self.cap:
                raise Budget('budget of %d instructions spent' % self.cap)


WRITE_OPEN = 202  # pimos.vmac:68 fep#write_open(string,?file,^st,?cdr)
BEEP = 113        # pimos.vmac:40 fep#beep(^st,?cdr)


def install_write_files(f):
    """fep#write_open (202) and the file's putb (111), flush (112) and
    close (60), for this process only: what is written is kept in
    f.written (path -> bytes), returned with the row's result.  fep.py
    serves no write-open (FepError, multialign_run's first run,
    OBSERVED 2026-11-26: pia_s2 writes its alignment to "test.res");
    the request's form is file_dvc.kl1:28-31's, the replies those of
    the read file's.  OURS, a home-file service of the runner"""
    orig, w, dirs = f.request, {}, {}
    f.written = {}

    def request(dev, msg):
        cmd = msg[0]
        if cmd == WRITE_OPEN and len(msg) == 5 and dev not in w and not f.known(dev):
            w[dev] = fepm.unjis(msg[4])
            f.written[w[dev]] = b''
            return [fepm.NORMAL]
        if dev in w and len(msg) <= 2 and cmd in (fepm.PUTB, fepm.FLUSH, fepm.CLOSE):
            if cmd == fepm.PUTB:
                f.written[w[dev]] += msg[1] if isinstance(msg[1], bytes) else b''
            if cmd == fepm.CLOSE:
                del w[dev]
            return [fepm.NORMAL]
        if dev in w and cmd == fepm.PATHNAME and len(msg) == 1:
            # fep#pathname (221) on a file opened by 202: the same
            # request as on a read file (bios/fep_module/file_dvc.kl1
            # device_io1 318-321; the read, write and append opens of
            # device_create/5, 21-44, all go on to the one reply/5 and
            # device_process/4; docs/fep_services.md 2.2), asked by unload after its write_open (consort, desq:
            # `unload([bignum_macro],"kl1>bignum_macro")`, FepError
            # before this, OBSERVED 2026-11-27).  The answer as a home
            # file's (longrun_ipl.add_home_file, 'PSI::' + the path +
            # '.1'): the version of a new file 1, INFERENCE.  OURS, the
            # runner's only, beside its write_open
            return [fepm.NORMAL, fepm.jis('PSI::%s.1' % w[dev])]
        if cmd == fepm.LISTING_ALL and len(msg) == 2 and isinstance(msg[1], bytes) \
                and msg[1] != fepm.LISTING_WILDCARD and dev in getattr(f, 'dirs', {}):
            # fep#listing_all (237) with a wildcard fep.py does not
            # serve (it serves "*.*" only, as the FEP tapes pin): the
            # entries of 204's listing that match it (wildcard_match),
            # in fep.listing's form.  The shell's pathname expansion
            # asks it with each node of the path and the last one's
            # wildcard (shell/utils/pathname.kl1 checkNode 254-271;
            # server/fep/file/dir_dvc.kl1 244-255 sends the wildcard as
            # given).  OURS, the runner's only (install_listing)
            pat = fepm.unjis(msg[1])
            names = [n for n in fepm.unjis(f.dirs[dev]).split('\n') if n]
            return [fepm.NORMAL, fepm.listing([n for n in names if wildcard_match(pat, n)])]
        if cmd == fepm.DIRECTORY and len(msg) == 5:
            # ".." resolved (cohlex's last `cd ..`: `Unable to change
            # directory ">sys>user>pmpsi>cohlex>.."`, 204 answered 5,
            # OBSERVED 2026-11-27; the shell sends the path with it,
            # INFERENCE that the FEP resolves it).  OURS
            if isinstance(msg[4], bytes):
                msg = list(msg[:4]) + [fepm.jis(resolve_parent(fepm.unjis(msg[4])))]
            dirs[dev] = msg[4]           # the path, for a 221 on it (below)
        if cmd == fepm.PATHNAME and len(msg) == 1 and dev in dirs \
                and dev in getattr(f, 'dirs', {}):
            # fep#pathname (221) on a directory device: the shell's cd
            # asks it (cohlex's `cd("cohlex")`, FepError before this,
            # OBSERVED 2026-11-26).  The answer as a file's, PSI:: and
            # the path (INFERENCE: a file's is longrun_ipl.add_home_file's
            # 'PSI::>sys>user>pmpsi>NAME.1').  OURS, the runner's only
            return [fepm.NORMAL, fepm.jis('PSI::' + fepm.unjis(dirs[dev]))]
        if cmd == BEEP and len(msg) == 1 and dev in f.windows:
            # fep#beep(^st,?cdr) on a window (pimos.vmac:40): answered
            # normal, no sound (mendels' `mendel .`, FepError before this,
            # OBSERVED 2026-11-26).  OURS, the runner's only
            return [fepm.NORMAL]
        return orig(dev, msg)
    f.request = request


def run_row(m, loaded, kind, row):
    # R7G's collection when memory runs out (pimm_gc.py), on: the prompt
    # machine has 56,367,129 free cells of 134,217,728, and a compile of
    # a few thousand lines fills them (mgtp_n, aya: `heap full` without
    # it, OBSERVED 2026-11-26).  The limit (the heap in use, cells):
    # the collector copies into the space above hp first, then back to
    # the bottom, alternately (pimm_gc.py: to = base when the live part
    # fits below lo, else hp), so the limit must fit in the memory left
    # above the prompt's heap, 56.4M cells, and twice over in the whole:
    # 50M.  The prompt's heap is past it already, so the first
    # collection is made at once.  A first version had 130M: the first
    # collection then came near the memory's end with no room for its
    # to-space (`gc: the to-space is full`, aya, laputa) or not at all
    # (`heap full`, mgtp_n, alignsa), OBSERVED 2026-11-26
    m.heap_limit = row.get('heap_limit', HEAP_LIMIT)
    m.gc_paths = None
    served = serve(row)
    install_listing()
    install_write_files(m.fep)
    log0 = len(m.fep.log)
    sink = Capped(row.get('budget', 50_000_000))
    kl1 = ','.join('"%s"' % n[:-4] for n in sorted(served) if n.endswith('.kl1'))
    typed = []
    for t in row['typed']:
        m_take = re.match(r'^\{TAKE (.+)\}$', t)
        typed += expand_take(m_take.group(1)) if m_take else [t.replace('{KL1}', kl1)]
    # the package work first, for every row that names no package itself
    # (ifs_rows.WORK: a compile or load into the login's pimos is refused,
    # `module registration error : pimos:: X`, OBSERVED for mgtp_n,
    # voronoi, editalign, mmi, pia_s2.exe).  OURS
    if not any('package' in t for t in typed):
        typed = [WORK] + typed
    # a row's `drop`: commands of an expanded file not typed (consort's
    # cd ">sys>user>desq": the files are served below the home, OURS)
    typed = [t for t in typed if not any(re.search(x, t) for x in row.get('drop', ()))]
    try:
        _o, _e, stop, dev = ls.play(m, loaded, kind, typed, sink)
    except Budget as e:
        stop, dev = 'BUDGET: %s' % e, m.fep
    win = ''.join(t for _d, t in dev.log[log0:])
    written = {p: fepm.unjis(b)[-20000:] for p, b in getattr(m.fep, 'written', {}).items()}
    return dict(name=row['name'], served=served, instructions=sink.instructions,
                stop=str(stop)[:400], window=win[-200000:], typed=typed,
                written=written)


# ---- the rows ---------------------------------------------------------

ROWS = {}


def row(name, **kw):
    """a row; alt=TYPED adds the row NAME+alt, the same files with other
    lines typed: the second stop, past a first one that is PIMOS's (the
    Listener's take) rather than the application's"""
    kw['name'] = name
    alt = kw.pop('alt', None)
    extra = kw.pop('serve_alt', [])     # files the second try serves besides
    budget_alt = kw.pop('budget_alt', None)
    ROWS[name] = kw
    if alt is not None:
        a = dict(kw, typed=alt, alt_of=name, name=name + '+alt',
                 serve=list(kw.get('serve', ())) + extra)
        if budget_alt:
            a['budget'] = budget_alt
        a.pop('static', None)
        ROWS[name + '+alt'] = a


from ifs_rows import define_rows, WORK  # noqa: E402

define_rows(row, archive)

# ---- classification ---------------------------------------------------

FLOAT = re.compile(r'float', re.I)


# A line of the window that is an error: the compiler's and loader's
# !ERROR!, the shell's syntax error and its `Module not found !!` (a goal
# whose module is not loaded), the loader's `Load Failed`
ERROR_MARK = re.compile(r'!ERROR!|Illegal|\*\*\* Syntax Error|Syntax error !!|Module not found !!|'
                        r'Load Failed|unable to open')


def is_error(ln):
    return bool(ERROR_MARK.search(ln))


def first_error(win):
    for ln in win.split('\n'):
        if is_error(ln):
            return ln.strip()
    return None


def classify(row, res):
    """(outcome, first stop) of a row: CLASSIFY in the header"""
    if 'static' in row:
        return row['static'][0], row['static'][1]
    stop, win = res['stop'], res['window']
    first = None
    if re.search(r'heap full|to-space is full', stop):
        # the model's memory, 134,217,728 cells with R7G's collection on:
        # full of live data (pimm_gc.py), not an instruction missing
        first = 'memory: ' + stop
    elif stop.startswith('refused:'):
        what = stop[len('refused:'):].strip()
        first = 'float: ' + what if FLOAT.search(what) else 'model: ' + what
    elif stop.startswith('FepError'):
        first = 'fep: ' + stop          # the FEP stand-in (ref/pimm/fep.py) lacks a service
    elif stop.startswith(('Fail', 'RuntimeError')):
        first = 'model: ' + stop
    ign = [re.compile(x) for x in row.get('ignore', ())]
    err = first_error('\n'.join(ln for ln in win.split('\n')
                                 if not any(x.search(ln) for x in ign)))
    if first is None and not err and stop.startswith('BUDGET'):
        first = 'budget'                # an error before the budget ran out is the stop
    if first is None and err:
        if re.search(r'undefined module|non existent module|not found|cannot open|no such|'
                     r'unable to open', err, re.I):
            first = 'missing: ' + err
        else:
            first = 'compile: ' + err
    if first is None:
        printed = row.get('printed', ())
        if printed:
            # compared without white space: the manuals' transcripts are
            # retyped ("Result=unsat", INSTALL.j:106, where the Listener
            # prints " Result = unsat")
            # the window and the files the run wrote (install_write_files)
            flat = re.sub(r'\s+', '', win + ''.join(res.get('written', {}).values()))
            ok = all(re.sub(r'\s+', '', p[0]) in flat for p in printed)
            outcome = 'RUNS-MATCHES' if ok else 'RUNS-DIFFERS'
        else:
            outcome = 'RUNS-NO-ORACLE'
        first = '-'
    elif first == 'budget':
        outcome = 'BUDGET'
    else:
        outcome = 'STOPS(float)' if first.startswith('float') else 'STOPS'
    if row.get('needs') == 'simpos':
        outcome = 'NEEDS-SIMPOS'
    elif row.get('needs') == 'other':
        outcome = 'NEEDS-OTHER'
    return outcome, first


def stop_class(first):
    """the histogram's key: the first stop without its operands"""
    if first is None or first.startswith('-'):
        return None
    if first.startswith('memory:'):
        # `heap full` (the memory's end) and `gc: the to-space is full`
        # (the collector's copy past it): one shortage
        return 'memory: the heap full'
    k = re.sub(r'\(.*', '', first)
    k = re.sub(r'(request \[\d+).*', r'\1]', k)   # the FEP request's code, not its operands
    k = re.sub(r'(device |at )\d+', r'\1N', k)
    return k[:90]


# ---- PINNED (OBSERVED, filled from the sweep run) ---------------------

from ifs_rows import PINNED  # noqa: E402



SUMMARY = os.path.join(HERE, '..', '..', 'docs', 'ifs_sweep_results.json')


def summarize(res):
    """what the classification reads of a result, small enough for git:
    the stop, the counts, every !ERROR! line (the first twenty), and the
    window's last 4,000 characters (every printed value of a row is in
    it, OBSERVED)"""
    win = res['window']
    errs = [ln.strip() for ln in win.split('\n') if is_error(ln)][:20]
    return dict(name=res['name'], instructions=res['instructions'], stop=res['stop'],
                typed=res['typed'], errors=errs,
                window='\n'.join(errs) + '\n...\n' + win[-4000:],
                written={p: t[-2000:] for p, t in res.get('written', {}).items()},
                loads=loads(win))


def loads(win):
    """[(file, 'Load Succeeded' or 'Load Failed')] of each load in a window
    (row objects: one entry per object file)"""
    out, cur = [], None
    for ln in win.split('\n'):
        m_ = re.search(r'Load File : \S+?::(?:>sys>user>pmpsi>)?(\S+)\.\d+\s*$', ln)
        if m_:
            cur = m_.group(1)
        elif cur and re.search(r'Load (Succeeded|Failed)', ln):
            out.append((cur, re.search(r'Load (Succeeded|Failed)', ln).group(0)))
            cur = None
    return out


def load_results(src, full=False):
    """name -> result: from a run's DIR (NAME.json each, summarized unless
    full) or a summary file"""
    if os.path.isdir(src):
        out = {}
        for name in ROWS:
            p = os.path.join(src, name + '.json')
            if os.path.exists(p):
                with open(p) as f:
                    res = json.load(f)
                out[name] = res if full else summarize(res)
        return out
    with open(src) as f:
        return json.load(f)


def table(results, rows=None, pinned=None):
    """[(name, outcome, first stop)] and the rows that differ from PINNED"""
    rows = rows or ROWS
    pinned = PINNED if pinned is None else pinned
    out, bad = [], []
    for name, r in rows.items():
        res = results.get(name)
        if res is None and 'static' not in r:
            out.append((name, 'NOT-RUN', '-'))
            bad.append(name + ' (not run)')
            continue
        o, first = classify(r, res)
        out.append((name, o, first))
        want = pinned.get(name)
        # pinned: the outcome and the first stop's class (stop_class: its
        # operands and addresses dropped, a FEP request's code kept)
        if want is None or want[0] != o or (stop_class(first) or first[:40]) != want[1]:
            bad.append('%s: %s %r, pinned %r' % (name, o, first[:80], want))
    return out, bad


def histogram(out, rows=None):
    """stop class -> the applications whose FIRST stop it is (rows that
    are not another row's variant), and -> those whose stop behind the
    first it is (the variants: +alt rows and rows with alt_of); each
    application once per class"""
    rows = rows or ROWS
    first, second = {}, {}
    for name, _o, stop in out:
        k = stop_class(stop)
        if not k:
            continue
        app = rows[name].get('alt_of', name)
        h = second if 'alt_of' in rows[name] else first
        if app not in h.setdefault(k, []):
            h[k].append(app)
    return first, second


def ranking(out, rows=None, md=False):
    """the main product: the first stops, ranked by how many applications
    each is the first stop of; for each application its next stop where
    a second try (alt row) shows one.  `budget` is no stop: those rows
    were still compiling or running, listed apart ("undetermined")"""
    rows = rows or ROWS
    first, second = histogram(out, rows)
    nxt = {}
    for k, apps in second.items():
        for a in apps:
            nxt.setdefault(a, []).append(k)
    lines = []
    ranked = sorted(((k, v) for k, v in first.items() if k != 'budget'),
                    key=lambda kv: (-len(kv[1]), kv[0]))
    if md:
        lines += ['| Rank | First stop | Applications | Each, with its next stop (second try) |',
                  '|---|---|---|---|']
    else:
        lines.append('first stops, ranked (application: next stop past it, where a second try ran)')
    for i, (k, apps) in enumerate(ranked, 1):
        each = ', '.join('%s%s' % (a, (' (next: %s)' % '; '.join(nxt[a])) if a in nxt else '')
                         for a in apps)
        if md:
            lines.append('| %d | `%s` | %d | %s |' % (i, k.replace('|', '\\|'), len(apps),
                                                    each.replace('|', '\\|')))
        else:
            lines.append('%3d  %s: %s' % (len(apps), k, each))
    und = first.get('budget', [])
    tail = 'undetermined, the budget spent with no stop (%d): %s' % (
        len(und), ', '.join('%s%s' % (a, (' (next: %s)' % '; '.join(nxt[a])) if a in nxt else '')
                            for a in und))
    lines.append('' if not md else '')
    lines.append(tail)
    # every stop met, first or next: what fixing it would also be needed for
    met = {}
    for h in (first, second):
        for k, apps in h.items():
            if k != 'budget':
                for a in apps:
                    if a not in met.setdefault(k, []):
                        met[k].append(a)
    lines.append('')
    lines.append('every stop met, first or next (applications it stands in front of):')
    for k, apps in sorted(met.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if len(apps) > 1 or k not in first:
            lines.append(('- `%s`: %d (%s)' if md else '%3d  %s: %s') % (
                (k, len(apps), ', '.join(apps)) if md else (len(apps), k, ', '.join(apps))))
    return lines


def report(argv):
    out, bad = table(load_results(argv[0]))
    for name, o, first in out:
        print('%-22s %-16s %s' % (name, o, first[:110]))
    counts = {}
    for name, o, _f in out:
        if 'alt_of' not in ROWS[name]:
            counts[o] = counts.get(o, 0) + 1
    print()
    for o in sorted(counts):
        print('%-16s %d' % (o, counts[o]))
    print()
    for ln in ranking(out):
        print(ln)
    if bad:
        print('ifs sweep: FAIL: ' + '; '.join(bad))
        return 1
    print('ifs sweep: PASS')
    return 0


def oracles(rows=None):
    """each printed value of a row, found in the archive file its citation
    names (the oracle is the archive's, not ours); returns the misses"""
    miss = []
    for name, r in (rows or ROWS).items():
        for pr in r.get('printed', ()):
            # (value as the window shows it, citation[, the text as the
            # archive prints it, when that differs: a table cell])
            value, cite = pr[0], pr[1]
            if len(pr) > 2:
                value = pr[2]
            fname = cite.split(':')[0].split(' ')[0]
            files = archive(r['archive'])
            hits = [n for n in files if n.endswith('/' + fname) or n == fname]
            if not hits:
                miss.append('%s: no %s in %s' % (name, fname, r['archive']))
                continue
            text = re.sub(r'\s+', '', b''.join(files[h] for h in hits).decode('latin-1'))
            v = re.sub(r'\s+', '', value)
            if v not in text and v.replace('=', '') not in text.replace('=', ''):
                miss.append('%s: %r not in %s' % (name, value, fname))
    return miss


def injections(results):
    """INJECTIONS: each a change to the rows or to a result, in this
    process only; each must make table() report exactly the rows named.
    OBSERVED 2026-11-27 against the committed summary after the second
    partial rerun (docs/ifs_apps.md 8; the first row with a model stop,
    h907_nseq since mgtp_n runs to its budget):
      h907_nseq's stop removed                       -> h907_nseq
      h907_nseq's stop made a float stop             -> h907_nseq, and
        classified `float:` (the float branch's own case)
      mgtp's printed value made its own window line
        ('21497 reductions': the match path)         -> mgtp
      `needs simpos` dropped from aligndp            -> aligndp
      ERROR_MARK made to match nothing               -> aya, gdcc, ldlib,
                                                        ldlib+alt, pmonitor,
                                                        pmonitor+alt
    and in check(): mgtp's printed value altered, the archive lookup
    (oracles())                                      -> mgtp.
    A source injection, applied by hand and reverted from a copy:
    classify() without its float branch failed --check on exactly the
    eight float rows of the first sweep (2026-11-26); against the
    rerun's summary, which has no float row, the same injection left
    --check PASS until the float case above checked the class, and with
    it fails that one case (OBSERVED 2026-11-27); after the second
    partial rerun mssd is a float stop again, and the injection fails
    --check on mssd's pin alone (OBSERVED 2026-11-27)."""
    import copy
    got = []
    base, bad0 = table(results)
    assert not bad0, bad0
    matches = [n for n, o, _f in base if o == 'RUNS-MATCHES']
    stops = [n for n, o, f in base if f.startswith('model: ') and not n.endswith('+alt')]
    cases = []
    if matches:
        n = matches[0]
        rows = copy.deepcopy(ROWS)
        pr = rows[n]['printed'][0]
        rows[n]['printed'][0] = (pr[0] + '9',) + tuple(pr[1:])        # a wrong expected result
        cases.append(('wrong printed value in %s' % n, rows, results, {n}))
    if stops:
        n = stops[0]
        res = copy.deepcopy(results)
        res[n]['stop'] = 'nothing left to run, 0 goals waiting'   # the stop lost
        cases.append(('stop of %s removed' % n, ROWS, res, {n}))
        res = copy.deepcopy(results)
        res[n]['stop'] = 'refused: b_floating_point_add at 1'      # another stop
        # and classified as one: since the float merge no row of the
        # summary stops at float, so this is what keeps classify()'s
        # float branch covered (docs/ifs_apps.md 8)
        cases.append(('stop of %s made a float stop' % n, ROWS, res, {n}, 'float'))
    differs = [n for n, o, _f in base if o == 'RUNS-DIFFERS' and n in results]
    if differs:
        n = differs[0]
        rows = copy.deepcopy(ROWS)
        last = [ln for ln in results[n]['window'].split('\n') if re.search(r'\d{3}', ln)][-1]
        rows[n]['printed'] = [(last, 'injected')]                   # the model's own output as the oracle
        cases.append(('printed value of %s made its window line %r' % (n, last.strip()),
                      rows, results, {n}))
    n = next(n for n, r in ROWS.items() if r.get('needs') == 'simpos' and 'static' not in r)
    rows = copy.deepcopy(ROWS)
    rows[n].pop('needs')                                        # the SIMPOS rule dropped
    cases.append(('needs simpos dropped from %s' % n, rows, results, {n}))
    # the classifier blind to the window's error lines: every row whose
    # first stop is one (compile:, missing:) and only those
    win_err = {n for n, _o, f in base if f.startswith(('compile:', 'missing:'))}
    cases.append(('ERROR_MARK made to match nothing', ROWS, results, win_err, 'blind'))
    ok = True
    global ERROR_MARK
    for case in cases:
        what, rows, res, want = case[:4]
        saved = ERROR_MARK
        if case[4:] == ('blind',):
            ERROR_MARK = re.compile(r'(?!x)x')
        try:
            out, bad = table(res, rows)
        finally:
            ERROR_MARK = saved
        caught = {b.split(':')[0].split(' ')[0] for b in bad}
        good = caught == want
        if case[4:] == ('float',):
            good &= all(o in ('STOPS(float)', 'NEEDS-SIMPOS', 'NEEDS-OTHER')
                        and f.startswith('float: ') for n_, o, f in out if n_ in want)
        ok &= good
        got.append('injection %s: reported %s (%s)' % (what, sorted(caught),
                                                      'as predicted' if good else 'NOT as predicted'))
    return ok, got


SERVICES = [
    # (what, the request, the answer wanted as text: a status, then the
    # reply's strings unjis'd); one device per directory or file opened
    ('the root', (60, [fepm.DIRECTORY, b'', b'pmpsi', b'', '>']), [1]),
    ('the root, listing("sys")', (60, [fepm.LISTING_ALL, 'sys']), [1, 'sys\n']),
    ('>sys>user', (61, [fepm.DIRECTORY, b'', b'pmpsi', b'', '>sys>user']), [1]),
    ('>sys>user, "*"', (61, [fepm.LISTING_ALL, '*']), [1, 'cgs\npmpsi\n']),
    ('HOME, listing("cohlex")', (62, [fepm.DIRECTORY, b'', b'pmpsi', b'', L.HOME]), [1]),
    ('HOME, "cohlex"', (62, [fepm.LISTING_ALL, 'cohlex']), [1, 'cohlex\n']),
    ('HOME, "*.*" (fep.py\'s own: every entry, the directory too)',
     (62, [fepm.LISTING_ALL, '*.*']), [1, 'cohlex\ntop.kl1.1\n']),
    ('HOME>cohlex, "*.mac"', (63, [fepm.DIRECTORY, b'', b'pmpsi', b'', L.HOME + '>cohlex']), [1]),
    ('HOME>cohlex, "*.mac" listed', (63, [fepm.LISTING_ALL, '*.mac']), [1, 'a.mac.1\n']),
    ('HOME>cohlex>a.mac.1 opened', (64, [fepm.READ_OPEN, b'', b'pmpsi', b'', L.HOME + '>cohlex>a.mac.1']),
     [1]),
    ('HOME>cohlex>a.mac.2 not', (65, [fepm.READ_OPEN, b'', b'pmpsi', b'', L.HOME + '>cohlex>a.mac.2']),
     [5]),
    ('HOME>cohlex>.. opened', (66, [fepm.DIRECTORY, b'', b'pmpsi', b'', L.HOME + '>cohlex>..']), [1]),
    ('HOME>cohlex>.., its pathname', (66, [fepm.PATHNAME]), [1, 'PSI::' + L.HOME]),
    ('>sys>other not', (67, [fepm.DIRECTORY, b'', b'pmpsi', b'', '>sys>other']), [5]),
    ('a written file', (68, [WRITE_OPEN, b'', b'pmpsi', b'', L.HOME + '>kl1>m.sav']), [1]),
    ('a written file, its pathname', (68, [fepm.PATHNAME]), [1, 'PSI::' + L.HOME + '>kl1>m.sav.1']),
]


def services_check():
    """the runner's directory and written-file services (install_listing,
    install_write_files) on a bare fep.Fep, no checkpoint: SERVICES'
    requests and answers.  The longrun_ipl state they wrap is restored
    after.  Returns the parts that differ.

    Observed injections (each into a private copy of ref/pimm, --check
    run on it, 2026-11-27; the services lines listed are all of them):
      the root and the way not served     the root and >sys>user: 204
        (served_dirs: HOME's only)        answered 5, then 237 FepError
                                          (4 lines)
      no wildcard listing (fep.py's       237 FepError for "sys", "*",
        "*.*" only)                       "cohlex", "*.mac" (4 lines)
      the wildcard matched against the    "*.mac" lists nothing (1 line)
        whole entry, version and all
      directories not listed              "sys", "*", "cohlex" list
                                          nothing, "*.*" lacks cohlex
                                          (4 lines)
      no versioned open                   a.mac.1 answered 5 (1 line)
      ".." not resolved                   HOME>cohlex>.. answered 5, its
                                          221 FepError (2 lines)
      no 221 on a written file            FepError (1 line)"""
    saved = (dict(L.HOME_FILES), dict(L._home), L.home_listing, L.kernel_file, dict(_abs))
    try:
        L.add_home_file('top.kl1', b'x.\n')
        L.add_home_file('cohlex>a.mac', b'x.\n')
        L.add_home_file('cohlex>b.kl1', b'x.\n')
        serve_abs('>sys>user>cgs>c.kl1', b'x.\n')
        # HOME with only these (the default home files set apart)
        for n in [n for n in L.HOME_FILES if n not in ('top.kl1', 'cohlex>a.mac', 'cohlex>b.kl1')]:
            del L.HOME_FILES[n]
        install_listing()
        f = fepm.Fep(lambda p: L.kernel_file(p), getb_unit=2, list_dir=lambda p: L.home_listing(p))
        install_write_files(f)
        bad = []
        for what, (dev, msg), want in SERVICES:
            msg = [fepm.jis(x) if isinstance(x, str) else x for x in msg]
            try:
                got = f.request(dev, msg)
            except fepm.FepError as e:
                got = ['FepError %s' % e]
            got = [fepm.unjis(x) if isinstance(x, bytes) else x for x in got]
            if got != want:
                bad.append('services: %s: %r, not %r' % (what, got, want))
        return bad
    finally:
        L.HOME_FILES.clear()
        L.HOME_FILES.update(saved[0])
        L._home.clear()
        L._home.update(saved[1])
        L.home_listing, L.kernel_file = saved[2], saved[3]
        _abs.clear()
        _abs.update(saved[4])


def check(argv):
    """the checkpoint-free check (run_tests.sh): the oracles against the
    archives, the committed summary against PINNED, the injections"""
    src = argv[0] if argv else SUMMARY
    results = load_results(src)
    miss = oracles()
    _out, bad = table(results)
    bad += services_check()
    ok, got = injections(results) if not bad else (False, [])
    # the oracle lookup itself: a printed value altered (a digit added to
    # its archive form) must be reported missing for that row alone
    import copy
    rows = copy.deepcopy(ROWS)
    n = next(n for n, r in rows.items() if r.get('printed'))
    pr = rows[n]['printed'][0]
    rows[n]['printed'][0] = (pr[0] + '9', pr[1]) + ((pr[2] + '9',) if len(pr) > 2 else ())
    caught = {x.split(':')[0] for x in oracles(rows)}
    good = caught == {n}
    ok &= good
    got.append('injection printed value of %s altered, archive lookup: reported %s (%s)'
               % (n, sorted(caught), 'as predicted' if good else 'NOT as predicted'))
    for g in got:
        print(g)
    print('oracles: %d printed values, %d not in their archive files' % (
        sum(len(r.get('printed', ())) for r in ROWS.values()), len(miss)))
    for x in miss + bad:
        print('  ' + x)
    if miss or bad or not ok:
        print('ifs sweep check: FAIL')
        return 1
    print('ifs sweep check: PASS (%d rows; the runner\'s FEP services, %d requests)'
          % (len(ROWS), len(SERVICES)))
    return 0


def markdown(argv):
    """the outcome table of docs/ifs_apps.md, from a run or the summary"""
    results = load_results(argv[0] if argv else SUMMARY)
    out, _bad = table(results)
    got = {n: (o, f) for n, o, f in out}

    def cell(x):
        return str(x).replace('|', '\\|').replace('\n', ' ')
    print('| Row | No. | Archive | Outcome | First stop | Second stop (+alt) | Typed (procedure) '
          '| Printed result | Last window line / stop |')
    print('|---|---|---|---|---|---|---|---|---|')
    for name, r in ROWS.items():
        if name.endswith('+alt'):
            continue
        o, f = got[name]
        alt = got.get(name + '+alt', ('', ''))[1] if name + '+alt' in ROWS else ''
        typed = '; '.join(r.get('typed', ())) if 'static' not in r else '(not run)'
        if len(typed) > 160:
            typed = typed[:157] + '...'
        typed = '`%s`' % typed.replace('`', "'") if 'static' not in r else typed
        printed = '; '.join('`%s` (%s)' % (p[0].strip().replace('\n', ' '), p[1])
                            for p in r.get('printed', ())) or 'none'
        res = results.get(name)
        last = ''
        if res:
            lines = [ln for ln in res['window'].split('\n') if ln.strip() and ln != '...']
            last = '%s instr.; %s' % (format(res['instructions'], ','),
                                      lines[-1][:90] if lines else res['stop'][:90])
        print('| %s | %s | `%s` | %s | %s | %s | %s | %s | %s |' % (
            name, r.get('no', '-'), r['archive'], o, cell(f[:120]), cell(alt[:100]),
            cell(typed), cell(printed), cell(last + ('; doc ' + r['doc'] if r.get('doc') else ''))))
    if any((results.get(n) or {}).get('loads') for n in ('objects', 'gdcc')):
        print('\nThe held objects, one line per file loaded (rows `objects` and `gdcc`):\n')
        print('| Row | Object | Result |')
        print('|---|---|---|')
        for n in ('objects', 'gdcc'):
            for f_, st in (results.get(n) or {}).get('loads', ()):
                print('| %s | `%s` | %s |' % (n, f_, st))
    print()
    for ln in ranking(out, md=True):
        print(ln)
    return 0


def write_summary(argv):
    """--summary DIR [OUT]: the summary (default docs/ifs_sweep_results.json);
    refused if it classifies any row otherwise than the full windows do.
    --summary --update DIR [OUT]: the committed summary with the rows run
    in DIR replaced (a partial rerun: the rows a model change can alter,
    those pinned at the stop it removes; 2026-11-27), the same refusal
    for the rows replaced"""
    update = argv[:1] == ['--update']
    if update:
        argv = argv[1:]
    results = load_results(argv[0])
    full = load_results(argv[0], full=True)
    a, _b = table(results, rows={n: r for n, r in ROWS.items() if n in results})
    b, _b = table(full, rows={n: r for n, r in ROWS.items() if n in results})
    assert a == b, [(x, y) for x, y in zip(a, b) if x != y]
    if update:
        merged = load_results(SUMMARY)
        merged.update(results)
        results = merged
    with open(argv[1] if len(argv) > 1 else SUMMARY, 'w') as f:
        json.dump(results, f, indent=0, sort_keys=True)
        f.write('\n')
    return 0


def run(argv):
    pkl, outdir = argv[0], argv[1]
    jobs, names, budget = 2, [], None
    rest = argv[2:]
    while rest:
        a = rest.pop(0)
        if a == '--jobs':
            jobs = int(rest.pop(0))
        elif a == '--budget':
            # the long runner: these rows with a larger budget (aya+alt's
            # compile, 14,441 lines, past 150M instructions; docs/ifs_apps.md)
            budget = int(rest.pop(0))
        else:
            names.append(a)
    names = names or [n for n, r in ROWS.items() if 'static' not in r]
    os.makedirs(outdir, exist_ok=True)
    m, loaded, _info, kind = ls.load(pkl)
    assert kind == 'prompt', 'ifs_sweep runs from a prompt checkpoint'
    m.ahead = False
    todo, running = list(names), {}
    while todo or running:
        while todo and len(running) < jobs:
            name = todo.pop(0)
            dest = os.path.join(outdir, name + '.json')
            pid = os.fork()
            if pid == 0:
                code = 1
                try:
                    r = dict(ROWS[name], budget=budget) if budget else ROWS[name]
                    res = run_row(m, loaded, kind, r)
                    with open(dest + '.tmp', 'w') as fh:
                        json.dump(res, fh)
                    os.rename(dest + '.tmp', dest)
                    code = 0
                except BaseException:
                    import traceback
                    traceback.print_exc()
                finally:
                    sys.stderr.flush()
                    os._exit(code)
            running[pid] = name
            ls.say('running %s (pid %d)' % (name, pid))
        pid, st = os.wait()
        name = running.pop(pid)
        ls.say('done %s: %s' % (name, 'ok' if st == 0 else 'FAILED %d' % st))
    return 0


def listing():
    for name, r in ROWS.items():
        how = 'static: ' + r['static'][0] if 'static' in r else 'run, budget %d' % r.get(
            'budget', 50_000_000)
        print('%-22s No.%-4s %-48s %s' % (name, r.get('no', '-'), r['archive'], how))


def main():
    a = sys.argv[1:]
    if not a or a[0] == '--list':
        listing()
        return 0
    if a[0] == '--run':
        run(a[1:])
        return report([a[2]])
    if a[0] == '--report':
        return report(a[1:] or [SUMMARY])
    if a[0] == '--summary':
        return write_summary(a[1:])
    if a[0] == '--check':
        return check(a[1:])
    if a[0] == '--markdown':
        return markdown(a[1:])
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main())
