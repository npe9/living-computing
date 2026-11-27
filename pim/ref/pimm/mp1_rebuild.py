#!/usr/bin/env python3
"""MP1 (docs/other_pims.md section 4): PIMOS rebuilt by its own compiler
on the model, and compared with the held object code.

    python3 ref/pimm/mp1_rebuild.py run PROMPT.pkl DIR [--jobs N]
                [--machine pimm|mpsi|both] [FILE ...]      (default pimm)
        each FILE (default: FILES below) compiled from the shell's prompt
        by the held compiler, through the home-file service, with
        pimos.h's machine set as asked; each compile in a forked process
        of its own, its result in DIR/MACHINE/NAME.json; then `report`
    python3 ref/pimm/mp1_rebuild.py report DIR
        per module: the pimm build against the held module, and the mpsi
        build against the pimm build; checked against PINNED
    python3 ref/pimm/mp1_rebuild.py inject PROMPT.pkl DIR
        the discriminating injections (INJECTIONS below)

STATUS 2026-11-26: part (a) run for the 25 files (about 20 min on four
processes); part (b), the mpsi builds, NOT run: the owner set
Multi-PSI aside before it was (one probe, hash.kl1 and rsc_init.kl1,
was; see "Findings").  `report` checks part (a) against PINNED.

Findings, part (a) (OBSERVED 2026-11-26, PINNED below):
  - 3 modules identical but for the header (scsi_conf, DAMC, comp);
  - 17 the same but for two orders and the header (same-but-order;
    18 with bufutil, below):
    the GC area's order and the key order in hash_on_constant slots
    and predicate-table chains (compare(); INFERENCE that the cause is
    the hash function and atom numbers, which are ours);
  - bufutil and token were refused at integer_to_floating_point
    until floating point was modelled (docs/float.md, 2026-11-26);
    re-run then, one file each: bufutil is the same but for the order
    (2396 cells against 2396), token differs (3180 cells against 3180,
    first difference the target of enqueue_goal at [1414], 59 lines,
    as mklib's and variable's);
  - 4 differ: token (above), hash, because the loaded hasher is the patch file's
    (pimm_patch_hash360E.sav), which lacks the extended_floating_point
    clause of hash0/4 that pimm's pimos.h switches on; the probe's mpsi
    build of hash.kl1 (extended_floating_point no) was identical to the
    patch but for the header, so the patch was built with that switch
    off; the base file's hasher (pimm_utility360E.sav, 405 cells)
    differs from both and was not explained.  mklib, variable and token: same
    size, first difference a branch target (enqueue_goal, execute):
    INFERENCE, predicates placed in another order, not checked.
  - The header: MagicNum (element 4) is [] in every held module, the
    IPL's decoder dropping it (lockstep_gca.py: Result is [[], Info |
    Elements]); ours is the compiler's 16#"00270001".  ModInfoVec
    (element 5) is the stamp: dates, times, the source path.  So no
    module is word for word; the cause is header and timestamps, plus
    the orders above, not relocation of code.
  - assemble_mode firm changes no code: rsc_init.kl1 compiled without
    the !set line differs from the firm build only in ModInfoVec.

Injections (inject; OBSERVED 2026-11-26), each on rsc_init.kl1 served
with one change, each `differs` where the change is and nowhere else:
  constant  predicate_to_code(Mod,go,3,..) -> 4: [63] put_integer 7,0,4
            against 7,0,3, 1 line
  external call  system_defined_servers:modules -> module: the GC entry
            ["ext", key 16843668 ...] against 16843007, 26 lines
  string    "Fep Server" -> "Fep Servex": the GC entry's string, 2 lines

PROMPT.pkl is the machine saved at the shell's prompt (bsv/README.md,
"The lockstep from a saved machine").  NOT part of run_tests.sh: the
pickle is ~1.2 GB and not in git, and a run takes about an hour on
three processes.  Reference model only; the compile route is R7's and
R8's (lockstep_shell.py play, APPS compile_work), which is in lockstep
on the core for those programs, not for these.

What is typed, at the shell's prompt (R7's lines, with two more):
    compile
    !set compile:assemble_mode firm
    !package pimos
    NAME
    !exit
`assemble_mode firm` (library/loader/selfcal.kl1:17-22, 114-117) lets
the compiler take the built-ins of class firm (library/compiler/blt.kl1,
e.g. tag_and_value) in a guard (depend.kl1 check_class); without it the
held compiler refuses sorter.kl1 with 96 `invalid guard goal` errors
(OBSERVED 2026-11-26).  How ICOT set it for the release is not held:
INFERENCE that it was firm or pimos, since the held modules use those
built-ins; the mode changes no code, only what is accepted
(it is read nowhere else in library/compiler or library/assembler).
`!package pimos` puts the module where the held one is, so the loader
fills in the same package atoms ("pimos:: NAME" Updated).

The home directory serves NAME.kl1, the 3.6 file from pimos.tar.Z byte
for byte (longrun_ipl.add_home_file: control bytes and EUC as there
said), and pimos.h, the 1995 copy from IFS d-pool (dpool_pimos.tgz,
src/owner-fixed/pimos.h; three identical copies), HELD but two years
younger than 3.6 (other_pims.md section 2.1).  As held it selects
`define(machine,pimm)`; for mpsi the one line is changed to
`define(machine,mpsi)` (OURS, the edit the file's own comment asks for:
"You can only select one machine").

The module made is caught at new_module (as r7_sieve.py does).  The held
module is the one already in memory with the same name atom: loaded at
the IPL's link from the held .sav by PIMOS's own decoder and loader
(longrun_ipl.py: every module the object of the last file holding it),
the same new_module.  Its code area is also checked word for word
against asm/unlsav.py's reading of the .sav file itself, so the held
side is the file, not only the model's load of it.

The comparison is cell by cell over the module object (loader.kl1
load/8: element 1 the GC area's size; then the GC area, whose first
four are the module's name, its package, MagicNum and ModInfoVec; the
predicate hash table; the code area).  An immediate cell (integer,
atom, instruction, predicate head) is compared as tag and value; a
pointer cell by what it points to (strings, vectors, lists read out);
a module cell by the module's name and package.  ModInfoVec is the
compile's stamp (library/utility/timstmp.kl1 new_stamp/4: compile date
and time, link date and time, the source file's name, its date and
time, the dependencies) and is reported apart: it differs by
construction.

Verdicts per module, pimm against held:
    identical          every cell equal, the stamp included (never
                       expected)
    identical-but-stamp every cell equal but ModInfoVec
    differs            the first differing cell: its index, region, the
                       two cells, and why if known
and mpsi against pimm: the same, with the count of differing cells.
"""
import json
import os
import struct
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import lockstep_shell as ls  # noqa: E402
import longrun_ipl as longrun  # noqa: E402
import pimm  # noqa: E402
import unlsav  # noqa: E402

DOCS = os.path.join(HERE, '..', '..', 'docs', 'nonlocal')
SRC_TAR = os.path.join(DOCS, 'pimos.tar.Z')
OBJ_TAR = os.path.join(DOCS, 'pimosobj.tar.Z')
DPOOL = os.path.join(DOCS, 'ifs', 'symbolic-proc', 'klic-apps', 'd-pool', 'dpool_pimos.tgz')
PIMOS_H = 'dpool/src/owner-fixed/pimos.h'
MACHINE_LINE = {'pimm': b':- define(machine,pimm).', 'mpsi': b':- define(machine,mpsi).'}

# The chosen set: every file of other_pims.md section 2.7's 26 with a
# switch whose value differs between mpsi and pimm (40 of the 41 sites),
# but macro/pimos/scsi/scsi.vmac (1 site), a macro file of the macro
# library pimos, which every compile here uses as the image holds it.
# These are the places (b) can change, so (a) checks the pimm branch of
# each against the held code.
FILES = (
    'bios/boot/bios.kl1', 'bios/boot/scsi_conf.kl1', 'bios/boot/scsi_man.kl1',
    'bios/scsi/DAM.kl1', 'bios/scsi/DAMC.kl1', 'bios/scsi/scsi_blt.kl1',
    'bios/scsi/scsi_common.kl1', 'bios/scsi/scsi_handler.kl1', 'bios/scsi/scsi_processor.kl1',
    'debugger/inspector/cmd_insp.kl1', 'debugger/inspector/cmd_mon.kl1',
    'debugger/inspector/inspvar.kl1', 'debugger/inspector/unify.kl1',
    'kernel/init/rsc_init.kl1',
    'library/unloader/decoder.kl1', 'library/unloader/encoder.kl1',
    'server/scsi/scsiRserver.kl1',
    'utility/ioutls/bufutil.kl1', 'utility/ioutls/mklib.kl1', 'utility/ioutls/token.kl1',
    'utility/ioutls/uparse.kl1', 'utility/ioutls/variable.kl1',
    'utility/pool/comp.kl1', 'utility/pool/hash.kl1', 'utility/sorter/sorter.kl1',
)

VMAC = 'macro/pimos/scsi/scsi.vmac'
# Part (a), the pimm builds against the held modules, OBSERVED
# 2026-11-26 (run ... --machine pimm, the default).  Part (b) is not
# pinned: Multi-PSI was set aside by the owner before it was run.
PINNED = {
    'bios': 'same-but-order', 'scsi_conf': 'identical-but-header',
    'scsi_man': 'same-but-order', 'DAM': 'same-but-order', 'DAMC': 'identical-but-header',
    'scsi_blt': 'same-but-order', 'scsi_common': 'same-but-order',
    'scsi_handler': 'same-but-order', 'scsi_processor': 'same-but-order',
    'cmd_insp': 'same-but-order', 'cmd_mon': 'same-but-order', 'inspvar': 'same-but-order',
    'unify': 'same-but-order', 'rsc_init': 'same-but-order', 'decoder': 'same-but-order',
    'encoder': 'same-but-order', 'scsiRserver': 'same-but-order',
    'bufutil': 'same-but-order',    # compiled since floats (2026-11-26, docs/float.md)
    'mklib': 'differs',         # first difference a branch target: not explained
    'token': 'differs',         # since floats: a branch target first, as mklib's
    'uparse': 'same-but-order',
    'variable': 'differs',      # first difference a branch target: not explained
    'comp': 'identical-but-header',
    'hash': 'differs',          # the loaded hasher is the patch: see the header
    'sorter': 'same-but-order',
}


def pimos_source(path):
    """the bytes of pimos/src/PATH in pimos.tar.Z"""
    data = subprocess.run(['uncompress', '-c', SRC_TAR], capture_output=True,
                          check=True).stdout
    import io
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        return t.extractfile('pimos/src/' + path).read()


def pimos_h(machine):
    with tarfile.open(DPOOL) as t:
        raw = t.extractfile(PIMOS_H).read()
    on = MACHINE_LINE['pimm']
    assert raw.count(on) == 1, 'pimos.h: the pimm line is not there once'
    if machine == 'pimm':
        return raw
    off = b'%' + MACHINE_LINE[machine]
    assert raw.count(off) == 1, 'pimos.h: no commented line for %s' % machine
    return raw.replace(on, b'%' + on).replace(off, MACHINE_LINE[machine])


# ---- reading a module object out of memory --------------------------

def canon(m, w, lo, hi, depth=0):
    """A cell as a JSON-able value: what is compared.  lo..hi is the
    module's own range (a code or module cell into it is relative)."""
    t = w[0]
    if t < 0x20:
        b = t & ~1
        if b in (pimm.INT, pimm.ATOM):
            return [t, w[1]]
        if b == pimm.REF or b in m.VAR_TAGS:
            d = m.deref(w)
            if m.unbound(d) or d[0] & ~1 in m.VAR_TAGS:
                return ['var']
            return canon(m, d, lo, hi, depth)
        if depth > 40:
            return ['deep']
        if b == pimm.LIST:
            return ['list', t & 1, canon(m, m.mem[w[1]], lo, hi, depth + 1),
                    canon(m, m.mem[w[1] + 1], lo, hi, depth + 1)]
        if b == pimm.STRG:
            size, els = m.string(w)
            return ['str', t & 1, size, els]
        if pimm.VECT0 <= b <= pimm.VECT0 + 14:
            n, a = m.vsize(w), m.vbase(w)
            return ['vec', t & 1] + [canon(m, m.mem[a + i], lo, hi, depth + 1) for i in range(n)]
        return ['ptr?', t, w[1]]
    if t == pimm.MOD:
        if lo <= w[1] <= hi:
            return ['mod-self']
        return ['mod', m.mem[w[1] + 2], m.mem[w[1] + 3]]
    if t == pimm.COD:
        if lo <= w[1] <= hi:
            return ['cod-self', w[1] - lo]
        return ['cod', w[1]]
    return [t, w[1]]


def module_cells(m, a):
    n = m.mem[a][1] & 0xffffff
    return [canon(m, m.mem[a + k], a, a + n) for k in range(n + 1)]


def regions(cells):
    """the region of each element: loader.kl1 load/8's layout"""
    gc = cells[1][1]
    names = {0: 'CDESC', 1: 'GC size', 2: 'module name', 3: 'package', 4: 'MagicNum',
             5: 'ModInfoVec'}
    mask = cells[2 + gc][1] if 2 + gc < len(cells) else 0
    out = []
    for i in range(len(cells)):
        if i in names:
            out.append(names[i])
        elif i < 2 + gc:
            out.append('GC area')
        elif i == 2 + gc:
            out.append('hash mask')
        elif i <= 2 + gc + mask + 1:
            out.append('hash index')
        elif cells[i][0] == pimm.PREDH or i > 2 + gc and any(
                c[0] == pimm.PREDH for c in cells[2 + gc:i]):
            out.append('code')
        else:
            out.append('entry table')
    return out


_SAV = []


def sav_modules():
    """(file, module name, code items) of every module of the held .sav
    set, read by asm/unlsav.py, once"""
    if not _SAV:
        import io
        data = subprocess.run(['uncompress', '-c', OBJ_TAR], capture_output=True,
                              check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(data)) as t:
            for mem in sorted(t.getmembers(), key=lambda x: x.name):
                if not mem.name.endswith('.sav'):
                    continue
                raw = t.extractfile(mem).read()
                words = list(struct.unpack('>%dH' % (len(raw) // 2), raw[:len(raw) // 2 * 2]))
                r = unlsav.Reader(words)
                r.rd()
                nm = r.rd()
                while r.peek() != 0xFFFF:
                    r.rd()
                r.rd()
                for _ in range(nm):
                    _ml, header, _gc, _hs, _preds, code = unlsav.parse_module(r)
                    _SAV.append((os.path.basename(mem.name), header[0][1], code,
                                 r.detail['code_size']))
    return _SAV


def held_sav_check(cells):
    """The held module's code area (its last code-size cells) against
    asm/unlsav.py's reading of the .sav files themselves, item by item:
    an instruction as tag and value, an integer as its value, an atom
    item by kind only (the file's atom numbers are the file's own), a
    table (hash_on_constant's, built by the loader) by its size, mask+1
    slots and two cells a key.  Returns 'FILE MODULE (N items, A atoms by
    kind, T tables)' for the module that agrees, or says none does."""
    found = []
    for fname, mname, code, size in sav_modules():
        if size > len(cells):
            continue
        p = len(cells) - size
        ok, atoms, tables = True, 0, 0
        for it in code:
            if p >= len(cells):
                ok = False
                break
            c = cells[p]
            step = 1
            if it[0] == 'inst':
                ok = c == [it[3], it[2]]
            elif it[0] == 'int':
                ok = c == [0, it[2] & 0xffffffff]
            elif it[0] == 'atomref':
                ok = isinstance(c[0], int) and c[0] & ~1 == pimm.ATOM
                atoms += 1
            elif it[0] == 'atom':
                ok = c[0] == 0x23
                atoms += 1
            elif it[0] == 'table':
                step = it[2] + 2 * it[3]
                tables += 1
            else:
                ok = False
            if not ok:
                break
            p += step
        if ok and p == len(cells):
            found.append('%s %s (%d items, %d atoms by kind, %d tables)' % (
                fname, mname, len(code), atoms, tables))
    return found[-1] if found else 'NO module of the held .sav set agrees'


# ---- one compile ----------------------------------------------------

class Count:
    """The trace, counted, not kept (r7_sieve.py's)."""
    def __init__(self):
        self.lines = 0
        self.instructions = 0

    def append(self, line):
        self.lines += 1
        if line[0] == 'I':
            self.instructions += 1


def compile_one(m, loaded, kind, path, machine, edit=None, mode='firm'):
    """compile PATH for MACHINE from the prompt; edit, (old, new) bytes,
    changes the served source first (the injections only)"""
    base = os.path.basename(path)
    name = base.rsplit('.', 1)[0]
    longrun.add_home_file('pimos.h', pimos_h(machine))
    src = pimos_source(path)
    if edit:
        assert src.count(edit[0]) == 1, edit
        src = src.replace(edit[0], edit[1])
    longrun.add_home_file(base, src)
    made = []
    builtin = m.builtin

    def watching(bname, ops, f, **kw):
        if bname == 'new_module':
            def g(*a):
                r = f(*a)
                made.append(r[0])
                return r
            return builtin(bname, ops, g, **kw)
        return builtin(bname, ops, f, **kw)
    m.builtin = watching
    before = set(a for a, c in m.mem.items() if c[0] == pimm.CDESC and c[1] >> 24 == 6)
    sink = Count()
    lines = ['compile'] + (['!set compile:assemble_mode ' + mode] if mode else []) + \
        ['!package pimos', name, '!exit']
    _ops, _ev, stop, dev = ls.play(m, loaded, kind, lines, sink)
    window = ''.join(t for _d, t in dev.log)
    out = dict(file=path, machine=machine, instructions=sink.instructions, stop=stop,
               window=window[window.find('** KL1 Compiler **'):], modules=[])
    for w in made:
        a = w[1]
        cells = module_cells(m, a)
        twins = [b for b in before if m.mem[b + 2] == m.mem[a + 2]
                 and m.mem[b][1] >> 24 == 6]
        mod = dict(name_atom=list(m.mem[a + 2]), cells=cells, held=[])
        for b in sorted(twins):
            mod['held'].append(dict(addr=b, cells=module_cells(m, b)))
        out['modules'].append(mod)
    return out


# The injections: rsc_init.kl1 (same-but-order in the real run),
# each served with one change made (the tree's file is not touched),
# compiled, and compared with the held module.  Each must be `differs`,
# and the first difference must be where the change is.
INJECTIONS = (
    ('constant', 'kernel/init/rsc_init.kl1', b'predicate_to_code(Mod,go,3,Code)',
     b'predicate_to_code(Mod,go,4,Code)'),
    ('external call', 'kernel/init/rsc_init.kl1', b'system_defined_servers:modules(Tail)',
     b'system_defined_servers:module(Tail)'),
    ('string', 'kernel/init/rsc_init.kl1', b'"Fep Server"', b'"Fep Servex"'),
)


def inject(argv):
    pkl, outdir = argv[2], argv[3]
    m, loaded, _info, kind = ls.load(pkl)
    m.ahead = False
    pids = {}
    for k, (label, path, old, new) in enumerate(INJECTIONS):
        dest = os.path.join(outdir, 'inject', '%d.json' % k)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        pid = os.fork()
        if pid == 0:
            code = 1
            try:
                with open(dest, 'w') as fh:
                    json.dump(compile_one(m, loaded, kind, path, 'pimm', (old, new)), fh)
                code = 0
            except BaseException:
                import traceback
                traceback.print_exc()
            finally:
                sys.stderr.flush()
                os._exit(code)
        pids[pid] = k
    while pids:
        pid, _st = os.wait()
        pids.pop(pid)
    bad = 0
    for k, (label, path, old, new) in enumerate(INJECTIONS):
        dest = os.path.join(outdir, 'inject', '%d.json' % k)
        if not os.path.exists(dest):
            print('injection %s: NO RESULT' % label)
            bad += 1
            continue
        with open(dest) as fh:
            r = json.load(fh)
        mod = r['modules'][-1]
        v = against('pimm', mod, mod['held'][-1])
        print('injection %s (%s -> %s): %s' % (label, old.decode(), new.decode(), v))
        bad += v != 'differs'
    print('mp1 rebuild injections: %s' % ('PASS' if not bad else 'FAIL'))
    return 1 if bad else 0


def run(argv):
    pkl, outdir = argv[2], argv[3]
    jobs, machines, files = 3, ('pimm',), []
    rest = argv[4:]
    while rest:
        a = rest.pop(0)
        if a == '--jobs':
            jobs = int(rest.pop(0))
        elif a == '--machine':
            v = rest.pop(0)
            machines = ('pimm', 'mpsi') if v == 'both' else (v,)
        else:
            files.append(a)
    files = files or list(FILES)
    m, loaded, _info, kind = ls.load(pkl)
    assert kind == 'prompt', 'mp1_rebuild runs from a prompt checkpoint'
    m.ahead = False
    todo = [(f, mc) for mc in machines for f in files]
    running = {}
    bad = 0
    while todo or running:
        while todo and len(running) < jobs:
            f, mc = todo.pop(0)
            dest = os.path.join(outdir, mc, os.path.basename(f).rsplit('.', 1)[0] + '.json')
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            pid = os.fork()
            if pid == 0:
                code = 1
                try:
                    res = compile_one(m, loaded, kind, f, mc)
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
            running[pid] = (f, mc)
            ls.say('compiling %s for %s (pid %d)' % (f, mc, pid))
        pid, st = os.wait()
        f, mc = running.pop(pid)
        ls.say('done %s for %s: %s' % (f, mc, 'ok' if st == 0 else 'FAILED %d' % st))
        bad += st != 0
    return report(['', '', outdir]) or (1 if bad else 0)


# ---- the comparison -------------------------------------------------

def show(c):
    s = json.dumps(c)
    return s if len(s) <= 80 else s[:77] + '...'


def cut(text, n=100):
    return text if len(text) <= n else text[:n - 3] + '...'


HEADER = (4, 5)     # MagicNum and ModInfoVec: see compare()


def gc_groups(cells):
    """The GC area after the header (elements 6 .. 1+size), split into
    its entries as loader.kl1 encode_gc_area lays them out: an external
    call is five cells (cache 0, module, hash key, module name,
    package), a module two (module, package), anything else one.
    Returns {element: (the entry's cells as JSON, offset in it)}."""
    gc = cells[1][1]
    top = 2 + gc
    out = {}
    p = 6
    while p < top:
        c = cells[p]
        key3 = cells[p + 2] if p + 2 < top else None
        if c == [0, 0] and cells[p + 1][0] in ('mod', 'var') and key3 \
                and isinstance(key3[0], int) and key3[0] & ~1 == pimm.ATOM:
            n = 5
        elif c[0] in ('mod', 'var'):
            n = 2
        else:
            n = 1
        # an external call is named by its hash key, module name and
        # package, not by its cache or module cells: those the loader
        # fills (a superseded held module's module cell is unbound)
        key = json.dumps(['ext'] + cells[p + 2:p + 5]) if n == 5 else json.dumps(cells[p:p + n])
        for k in range(n):
            out[p + k] = (key, k)
        p += n
    return out


GC_OPS = (0x37, 0x62, 0x66)


def s16(v):
    return (v & 0xffff) - (0x10000 if v & 0x8000 else 0)


def gc_ref(cells, groups, i):
    """If code cell i names a GC area element (its low 16 bits an
    offset from the cell: element = i + offset + 2, the reading that
    makes every such cell of rsc_init agree, OBSERVED 2026-11-26), that
    element's entry; else None.  Only the instructions whose operand is
    a GC offset (docs/kl1_encoding.md types r_c16_scnst and c8_c16_ext:
    put_structured_constant 37h, execute_external 62h,
    enqueue_goal_external 66h)."""
    c = cells[i]
    if not isinstance(c[0], int) or c[0] != 0x23 or c[1] >> 24 not in GC_OPS:
        return None
    t = i + s16(c[1]) + 2
    return groups.get(t)


def entries(groups):
    """the GC area's entries, as a sorted list (a multiset)"""
    return sorted(k for k, o in groups.values() if o == 0)


def compare(ours, theirs):
    """(verdict, None, 0 or 1, number of cells that differ only by an
    order).  Verdicts:
        identical            every cell equal
        identical-but-header every cell equal but MagicNum and ModInfoVec
        same-but-order       norm_lines equal: equal once the GC area's
                             order and the order of the keys in a
                             hash_on_constant slot are undone
        differs              otherwise

    The GC area's order is the order of the assembler's address table,
    kl1cmp_my_pool:keyed_bag get_all (library/assembler/add_tab.kl1,
    my_pool.kl1): by bucket, hasher:hash(Key) /\\ 255, and hasher:hash
    of an atom or a string is the built-in hash, whose PIM/m function is
    lost (pimm.py i_hash: PDSS's, OURS) and whose atom numbers are
    new_atom's (OURS).  INFERENCE: so the order is the model's, not the
    compiler's (what is shown is that the entries and the offsets that
    name them agree, not why the order differs).  A hash_on_constant
    slot's keys are a list in the order they were put in it; the held
    module's were put in by the loader from the file's table, ours by
    the assembler, both into slots chosen by our atom numbers.  So are
    the chains of the predicate table (entry_table): the loader makes
    them from the list it is given, the file's order or the compiler's."""
    if ours == theirs:
        return 'identical', None, 0, 0
    raw = [i for i in range(max(len(ours), len(theirs)))
           if i not in HEADER and (i >= len(ours) or i >= len(theirs) or ours[i] != theirs[i])]
    if not raw:
        return 'identical-but-header', None, 0, 0
    if [t for _i, t in norm_lines(ours)] == [t for _i, t in norm_lines(theirs)]:
        return 'same-but-order', None, 0, len([i for i in raw if i >= 6])
    return 'differs', None, 1, 0


HOC = 0x2d      # hash_on_constant (docs/kl1_encoding.md; pimm.py i_hash_on_constant)


def hash_table(cells, i):
    """hash_on_constant at i: (its lines, the last cell of its table).
    Word 1 its miss label; then mask+1 slots, each {atom 0} or {integer,
    count << 16 | offset} to count {key, offset} pairs (pimm.py
    i_hash_on_constant).  A slot's pairs are given sorted, targets as
    offsets from the instruction."""
    mask = cells[i][1] & 0xffff
    miss = i + 1 + 2 + s16(cells[i + 1][1])
    lines = ['hash_on_constant %08x miss %+d' % (cells[i][1], miss - i)]
    end = i + 2 + mask
    for k in range(mask + 1):
        sl = i + 2 + k
        st = cells[sl]
        if st[0] != pimm.INT:
            lines.append('  slot %d %s' % (k, json.dumps(st)))
            continue
        count, off = st[1] >> 16, st[1] & 0xffff
        pairs = []
        for j in range(count):
            e = sl + off + 2 * j
            pairs.append((json.dumps(cells[e]), e + 2 + s16(cells[e + 1][1]) - i))
            end = max(end, e + 1)
        lines.append('  slot %d %s' % (k, sorted(pairs)))
    return lines, end


def entry_table(cells, top):
    """The predicate table at element top (loader.kl1 set_pred_table:
    the mask, mask+1 index cells, each 0 or count << 16 | offset to its
    chain, then the chains' {key, offset} pairs, a predicate's code at
    the offset cell + offset), as lines, slot by slot with each chain's
    pairs sorted (the loader puts them in the order the compiler or
    the file lists them); and the element after it."""
    mask = cells[top][1]
    lines = ['hash mask %d' % mask]
    end = top + 1 + mask
    for k in range(mask + 1):
        ix = top + 1 + k
        v = cells[ix][1]
        if cells[ix] == [0, 0]:
            lines.append('  entries %d none' % k)
            continue
        count, off = v >> 16, v & 0xffff
        pairs = []
        for j in range(count):
            q = ix + off + 2 * j
            pairs.append((json.dumps(cells[q]), q + 1 + s16(cells[q + 1][1])))
            end = max(end, q + 1)
        lines.append('  entries %d %s' % (k, sorted(pairs)))
    return lines, end + 1


def norm_lines(cells):
    """The module as lines that do not depend on the two orders compare()
    undoes: the header's own cells (not MagicNum or ModInfoVec), the GC
    area as its entries sorted, then every later cell; a code cell
    naming a GC element by that entry (gc_ref), a hash_on_constant's
    table slot by slot (hash_table), an instruction disassembled
    (asm/kbndis.py)."""
    import kbndis
    groups = gc_groups(cells)
    top = 2 + cells[1][1]
    im = kbndis.Image()
    im.cells = [tuple(c) if isinstance(c[0], int) else (pimm.STRG, 0) for c in cells] + [(0, 0)] * 4
    im.mods = [dict(addr=-1, length=len(cells) - 1, preds=[], name='', package='')]
    out = [(1, 'gc size %d' % cells[1][1]), (2, show(cells[2])), (3, show(cells[3]))]
    for key in entries(groups):
        out.append((6, 'gc entry ' + key))
    code0 = min([i for i, c in enumerate(cells) if c[0] == pimm.PREDH] or [len(cells)])
    lines, i = entry_table(cells, top)
    out += [(top, t) for t in lines]
    while i < len(cells):
        c = cells[i]
        if i >= code0 and c[0] == 0x23 and c[1] >> 24 == HOC:
            lines, end = hash_table(cells, i)
            out += [(i, t) for t in lines]
            i = end + 1
            continue
        r = gc_ref(cells, groups, i) if i >= code0 else None
        if r is not None:
            text = '%04x.... -> %s +%d' % (c[1] >> 16, r[0], r[1])
        elif isinstance(c[0], int) and c[0] == 0x23:
            try:
                text = im.dis(i)
            except Exception:
                text = show(c)
        else:
            text = show(c)
        out.append((i, text))
        i += 1
    return out


def first_diff(ours, theirs):
    """(index in ours, index in theirs, line ours, line theirs, lines
    differing) of the first difference of norm_lines, or None"""
    import difflib
    a, b = norm_lines(ours), norm_lines(theirs)
    sm = difflib.SequenceMatcher(None, [t for _i, t in a], [t for _i, t in b], autojunk=False)
    ops = [o for o in sm.get_opcodes() if o[0] != 'equal']
    if not ops:
        return None
    n = sum(max(i2 - i1, j2 - j1) for _t, i1, i2, j1, j2 in ops)
    _t, i1, _i2, j1, _j2 = ops[0]
    la = a[i1] if i1 < len(a) else (len(ours), '(end)')
    lb = b[j1] if j1 < len(b) else (len(theirs), '(end)')
    return la[0], lb[0], la[1], lb[1], n


SWITCHES = ('fep_interface', 'ipl_parameter', 'extended_floating_point')


def sites(path):
    """the lines of PATH with a switch whose value differs between mpsi
    and pimm in pimos.h (other_pims.md section 2.7's count)"""
    out = []
    for k, line in enumerate(pimos_source(path).decode('latin1').split('\n'), 1):
        t = line.replace(' ', '')
        for sw in SWITCHES:
            if t.startswith(':-switch(%s)' % sw):
                out.append('%d %s' % (k, sw))
    return out


def load_results(outdir, machine):
    res = {}
    d = os.path.join(outdir, machine)
    if not os.path.isdir(d):
        return res
    for fn in sorted(os.listdir(d)):
        if fn.endswith('.json'):
            with open(os.path.join(d, fn)) as fh:
                res[fn[:-5]] = json.load(fh)
    return res


def against(label, mod, h):
    v, _first, _n, order = compare(mod['cells'], h['cells'])
    line = '    %-5s against held @%x (%s): %s, %d cells vs %d' % (
        label, h['addr'], held_sav_check(h['cells']), v, len(mod['cells']), len(h['cells']))
    if order:
        line += ', %d cells in another order' % order
    print(line)
    if v == 'same-but-order':
        raw = [i for i in range(len(mod['cells']))
               if i not in HEADER and mod['cells'][i] != h['cells'][i]]
        i = raw[0]
        go = gc_groups(mod['cells'])
        why = ('the GC area\'s order' if i in go or gc_ref(mod['cells'], go, i)
               else 'a hash_on_constant slot\'s key order')
        print('      first word not equal: [%d] ours %s | held %s: %s (an order, not a code'
              ' difference)' % (i, show(mod['cells'][i]), show(h['cells'][i]), why))
    if v == 'differs':
        d = first_diff(mod['cells'], h['cells'])
        if d:
            print('      first difference: ours [%d] %s | held [%d] %s; %d lines differ' % (
                d[0], cut(d[2]), d[1], cut(d[3]), d[4]))
    return v


def report(argv):
    outdir = argv[2]
    pimm_r, mpsi_r = load_results(outdir, 'pimm'), load_results(outdir, 'mpsi')
    got = {}
    print('MP1(a): each build against the held module(s) of the same name')
    names = [os.path.basename(f).rsplit('.', 1)[0] for f in FILES]
    for name in names + sorted(set(pimm_r) - set(names)):
        if name not in pimm_r:
            print('  %-16s NO RESULT (the compile did not finish: see the run\'s log)' % name)
            got[name] = 'no result'
            continue
        r = pimm_r[name]
        if not r['modules']:
            print('  %-16s NO MODULE MADE: %s' % (name, r['stop']))
            got[name] = 'none'
            continue
        mod = r['modules'][-1]
        print('  %s (%s, %d instructions)' % (name, r['file'], r['instructions']))
        if not mod['held']:
            print('    no held module of that name')
            got[name] = 'no held'
            continue
        for k, h in enumerate(mod['held']):
            v = against('pimm', mod, h)
            if k == len(mod['held']) - 1:
                got[name] = v            # the loaded one: the last file's
        last = mod['held'][-1]
        for i in HEADER:
            if mod['cells'][i] != last['cells'][i]:
                print('      [%d] ours %s | held %s' % (i, show(mod['cells'][i]), show(last['cells'][i])))
        if name in mpsi_r and mpsi_r[name]['modules']:
            for h in mod['held']:
                v = against('mpsi', mpsi_r[name]['modules'][-1], h)
                if h is last:
                    got['mpsi~held:' + name] = v
    if mpsi_r:
        print('MP1(b): the mpsi build against the pimm build')
    total = 0
    for name in (names + sorted(set(mpsi_r) - set(names))) if mpsi_r else ():
        if name not in mpsi_r:
            print('  %-16s NO RESULT' % name)
            got['mpsi:' + name] = 'no result'
            continue
        r = mpsi_r[name]
        total += len(sites(r['file']))
        if name not in pimm_r or not r['modules'] or not pimm_r[name]['modules']:
            print('  %-16s not compared (%s)' % (name, r['stop']))
            got['mpsi:' + name] = 'none'
            continue
        a, b = r['modules'][-1]['cells'], pimm_r[name]['modules'][-1]['cells']
        v, _first, _n, _order = compare(a, b)
        got['mpsi:' + name] = 'differs' if v == 'differs' else 'same'
        st = sites(r['file'])
        print('  %-16s %-8s %5d cells, pimm %5d; switch sites: %s' % (
            name, got['mpsi:' + name], len(a), len(b), ', '.join(st) or 'none'))
        if v == 'differs':
            d = first_diff(a, b)
            if d:
                print('      first difference: mpsi [%d] %s | pimm [%d] %s; %d lines differ' % (
                    d[0], cut(d[2]), d[1], cut(d[3]), d[4]))
    if mpsi_r:
        vmac = len(sites(VMAC))
        print('switch sites: %d in the files compiled, %d in %s (not compiled: the macro'
              ' library pimos in the image is the pimm build, so its fep_interface switch is'
              ' pimm\'s in every mpsi build here); %d in all (other_pims.md section 2.7: 41)'
              % (total, vmac, VMAC, total + vmac))
    counts = {}
    for k, v in got.items():
        side = k.split(':')[0] if ':' in k else 'pimm~held'
        counts[(side, v)] = counts.get((side, v), 0) + 1
    print('counts:', ', '.join('%s %s %d' % (s, v, n) for (s, v), n in sorted(counts.items())))
    if PINNED:
        wrong = [(k, PINNED.get(k), got.get(k)) for k in sorted(set(PINNED) | set(got))
                 if PINNED.get(k) != got.get(k) and ':' not in k]
        if wrong:
            print('mp1 rebuild: FAIL', wrong)
            return 1
    print('mp1 rebuild: PASS' if PINNED else 'mp1 rebuild: (nothing pinned)')
    print('got = %r' % got)
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'run':
        sys.exit(run(sys.argv))
    if cmd == 'report':
        sys.exit(report(sys.argv))
    if cmd == 'inject':
        sys.exit(inject(sys.argv))
    raise SystemExit(__doc__)
