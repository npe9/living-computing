#!/usr/bin/env python3
"""The long run: the IPL loads and links the whole of pimos.ipl.

    python3 ref/pimm/longrun_ipl.py --script FILE [N]   write the script
    sim_pimm_driver | python3 ref/pimm/longrun_ipl.py compare [N]
    python3 ref/pimm/longrun_ipl.py --reference [N]     reference model alone
    python3 ref/pimm/longrun_ipl.py --reference --go    ... and then PIMOS is entered
    python3 ref/pimm/longrun_ipl.py --reference --go --fep   ... with the device attached
    python3 ref/pimm/longrun_ipl.py --reference --save FILE [--go [--fep]]
                                    the machine after the (checked) link, pickled
    python3 ref/pimm/longrun_ipl.py --load FILE --go [--fep]
                                    from that machine straight to --go (seconds,
                                    not the IPL's ~15-50 min; FILE ~1.1 GB)
    python3 ref/pimm/longrun_ipl.py --load FILE --go --fep --type LINE [--type LINE ...]
                                    ... and the lines typed into the shell's
                                    window after the login, in order
    python3 ref/pimm/longrun_ipl.py --load FILE --go --fep --save-prompt FILE2 [--type ..]
                                    ... and the machine at the shell's prompt
                                    (run dry after the login, the window's getl
                                    held) saved to FILE2, for lockstep_shell.py
                                    (~85 s; FILE2 ~1.2 GB)

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
After the merger timing change (2026-11-24): 73,594,186 heap cells,
the rest the same (837 s to the script on a shared machine).
On BOTH models (bsv/run_pimm_longrun.sh), 2026-11-23: the whole list,
447,739,516 trace lines identical, every check above passing; 7,350 s
on a machine shared with other runs (668 s of it making the script).
That run's simulator was built from the tree of b7187d59, before the
merger timing change of 2026-11-24 (docs/pimm_semantics.md, merge),
which moved the count.  Run again 2026-11-24 under the merger rule
(the simulator built from the tree of 3712bdd9): 448,194,526 trace
lines identical, every check passing, 7,435 s to the compare on a
shared machine (546 s of it making the script).

--go (reference model alone, with what only it has: Machine.ahead):
after the link, top:go_pimos1(Loaded, BootInfo) is started as the IPL
would, apply(Code, {BootInfo, Atoms, Modules, Comments}), and run
until the model refuses something.  It is NOT the IPL's boot: the
goal is started by the bench outside any shoen, and no device is
attached.  BootInfo was an unbound variable until 2026-11-23; since
then it is made by the IPL's own ipl:make_boot_info/1, spawned beside
the goal as ipl:boot0 makes it (docs/binary_reverse_engineering.md
1.3, item 11): with it unbound, bios.kl1's create_os_device/3 met an
unbound cluster at its @node(Cluster).  Observed 2026-11-23:
pim:go/4 runs 1,244 instructions in the loaded modules, the console
is given "PIMOS V 3.600 20-May-93" (display_console; the text the
source's default branch gives, bios/boot/bios.kl1 and
kernel/init/version.kl1), and it stops at scsi_where (22:A0, not
implemented).  The check is the banner; the stop is printed, since it
moves as the model grows.  Later (scsi_where implemented): 1,722
instructions, the stop scsi_init: no device attached (1,791 with
make_boot_info, which runs first).

--fep (rung S0 of docs/scsi_plan.md): the device ref/pimm/fep.py is
attached as ref_scsi.py attaches it (Machine.fep), and when the
machine has nothing left to run the SCSI commands that wait for the
device are given it again (Machine.scsi_poll), until neither moves.
Each run is given limit 10**12 (both with and without --fep); a run
that ends with goals suspended is reported "nothing left to run, N
goals waiting".  The FEP's messages are printed in order.  Observed
2026-11-23 (--save, then --load ... --go --fep, the same): 3,612
instructions; scsi_init passed; NO scsi_command issued, so the FEP
conversation is empty; console the banner only; the stop is the
guard instruction multiply (23:F6) at cell 62160538, in
scsi:check_lun/4 (bios/scsi/scsi_handler.kl1:119-122, LUN =<
ExtLUN*2040+7; ExtLUN = 4, scsi_init's Info element 2, OURS), for
unit 0 LUN 0 of the kernel's bus scan.  docs/binary_reverse_
engineering.md 1.4, "The kernel's FEP conversation".  Later the same
day (the instructions met implemented on both models, fep.py's
answers for the bus scan, make_boot_info): 12,912 instructions, 8 SCSI
commands (the bus scan: unit 7 found, 5..0 absent), no FEP packet, the
console the banner alone; the stop enqueue_goal_to_processor with an
unbound node number in scsi_manager:check_lpid_pool/7 (1.4).
2026-11-24 (that goal waits, from VPIM; system_timer, set_timer,
signed write_integer, wait_vector_0, apply with {}, diff of a
structure; fep.py's append_open): 23,348 instructions, 10 SCSI
commands, the first FEP message (append_open of pimos:pimos.syslog),
the console the banner alone; the stop jump, not implemented.
2026-11-24, a cached machine made afresh with --save (23,348 at jump
again): jump, set_marked_variable, wait_vector, the timer device's
create_timer and get_date_time (fep.py), multiply_bignum_by_word:
65,482 instructions, the console the banner alone; the stop
subtract_bignum(32#{}, 32#{0}), the 32#{0} from the clock at 0.
2026-11-24, the clock advancing (one tick every 423 instructions):
subtract_bignum, the timer's close (fep.py), get_constant, body
vector/3, code_to_predicate, the unification of long vectors,
add_shoen_resource: 92,797 instructions, the console the banner alone;
the stop fep_attributes (240) on a file device (FepError).
2026-11-24, the login (docs/fep_services.md §6, §7): fep.py answers
240, the pimos: files (kernel_file below: the held object's, 5 for
what is not there and for me: and the home directory), the
string-I/O devices of the login service and the window calls.  When
the machine has run dry and no waiting command moves, the device is
asked for its next scripted event (Fep.idle()): the first is the
login of §7.5, the answer to the local server's held io(1); the run
stops when the script is empty.  With search_character, unbound,
extended_floating_point, module, the double-precision integers,
allow_shoen_resource_report, the bignum guards, apply and
enqueue_goal of more than 16, and create_shoen's distributed form, on
both models: 8,587,072 instructions with the login ID 0 (fep.py LOGIN,
2026-11-24, docs/fep_services.md 6.5; 8,587,092 with the ID 1 before
it; 8,586,110 before the merger
timing change of 2026-11-24, docs/pimm_semantics.md merge; the cache
made afresh under it); the console "LOCAL  LOGIN
SERVICE STARTS ***", 0, "CANNOT MAKE A TCPIP LOGIN SERVICE!!", 0; the
replier's texts and the window's "Shell>> " in the device's log; the
stop "nothing left to run, 1,220 goals waiting", the window's getl
(110) held.
With --type LINE (any number): each line answers the next held getl
(fep.py's event list, OURS).  --type shutdown --type yes: the shell
takes "shutdown" and the job starts shutdown_body:go, which takes its
third branch: the string-I/O window pimos_standard_io_window, titled
SHUTDOWN, asks "Really(yes/no)?" and the second line answers it; the
console then shows "Shutdown started", "User Server End",
"Statistics in PIMOS:", 0, 790104, "PIMOS END********" and the run
ends at 8,766,319 instructions (8,766,339 with the login ID 1), nothing left to run, 253 goals
waiting (docs/binary_reverse_engineering.md 1.4, "A command typed",
with the manual compared line by line; before the merger timing
change a wait cycle through the user table stopped it at 8,673,642).
--type 'cat <= file("pimos:pimos.groups")': the file read through
pimos: and written to the window, then Shell>> again: 8,760,665
instructions (8,760,685 with the login ID 1), 1,224 goals waiting.

N: only the first N files of the list (for a shorter trial; the link
is then normal only if those files are closed under their calls).
"""
import copyreg
import os
import pickle
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import fep as fepm  # noqa: E402
import pimm  # noqa: E402
import lockstep_cons as cons  # noqa: E402
import lockstep_ipll as ipll  # noqa: E402
import lockstep_link as link  # noqa: E402
import lockstep_modc as modc  # noqa: E402

# lines: the Bluesim run of 2026-11-24 under the merger rule (the merger
# acts at unification, docs/pimm_semantics.md merge), 448,194,526; it was
# 447,739,516 before that change, which moved it (every lockstep count
# after a merger moved).  The other values are the reference's, unchanged
PINNED = dict(files=20, modules=480, atoms=10032, replaced=8, stay=8, lines=448194526)
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


class GoTrace(list):
    """The trace of --go: the console's lines (C, S) are kept, the
    instructions counted, nothing else kept (a long run's trace would
    not fit)."""
    instructions = 0

    def append(self, line):
        if line[0] == 'I':
            self.instructions += 1
        elif line[0] in 'CS':
            list.append(self, line)


# The files of pimosobj.tar.Z's object/ (docs/nonlocal, not in git):
# its object/INSTALL (lines 8-9) copies object/* to pimos:, so
# pimos:NAME is served as object/NAME, byte for byte (the held text
# files are 16-bit JIS, as SIMPOS keeps text; the file server widens
# what getb gives, server/fep/file/file_dvcb.kl1 return_values_buffer).
# A name the set does not hold is answered abnormal (5), as for
# pimos:autoload.tbl, which the shipped set does not have
# (docs/fep_services.md 7.2).  me: is user:pmpsi, which holds only
# SIMPOS's init.com and login.com (INSTALL:9), and a home directory
# (">sys>user>" ++ RN, the string fep.py's simpos_user_device gives)
# holds nothing INSTALL puts there: both answered 5 (fep_services.md
# 7.2, 7.5), so the shell takes its default prompt.  Other names
# still raise.
PIMOSOBJ = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'pimosobj.tar.Z')
_held = {}


def held_object(name):
    """object/NAME of pimosobj.tar.Z, or None."""
    if not _held:
        import io
        import subprocess
        import tarfile
        raw = subprocess.run(['uncompress', '-c', PIMOSOBJ], capture_output=True,
                             check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(raw)) as t:
            for e in t.getmembers():
                if e.isfile() and e.name.startswith('object/'):
                    _held[e.name[len('object/'):]] = t.extractfile(e).read()
    return _held.get(name)


# The home directory's files (2026-11-25, R7: the primer's sample1):
# HOME (">sys>user>pmpsi", fep.py simpos_user_device) holds the one
# file the primer has the reader make there, sample1.kl1 ("should be
# entered into a file named sample1.kl1", primer25.tex:585-605, the
# PIMOS 2.5 primer; docs/nonlocal/ifs/manuals/pimos/primer25.tex.Z,
# in git), its text read from the primer at run time, the verbatim
# block's lines 592-605 as printed, each ended by an LF (16-bit JIS,
# element 10, as the held text files, e.g. object/pimos.conf).  What
# the FEP says of it (fep.FileData):
#   221, its pathname: NODE::PATH.VERSION, the form the primer's own
#     compile prints, "Compile File : **psi***::>sys>**>sample1.kl1.1"
#     (primer25.tex:1280; the compiler prints 221's answer,
#     library/loader/dstrbt.kl1 distribute/5, assign_pre_proc/9), and
#     the form of every held source's first line ("icpsi183::>sys>user>
#     hori>...>fileutil.kl1.10").  The node "PSI" (fep.ATTRIBUTES' Host)
#     and the version 1 are OURS;
#   222, its attributes (fep.attribute_string): the owner and the
#     updater the SIMPOS user pmpsi, created and modified 20-May-93
#     00:00:00 (the FEP's DATE), 1 link, FSize the file's bytes, RSize
#     0: all OURS, in the format PIMOS reads.
HOME = '>sys>user>' + fepm.LOGIN['rn']
PRIMER = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'ifs', 'manuals', 'pimos',
                      'primer25.tex.Z')
HOME_FILES = {'sample1.kl1': (PRIMER, 592, 605, ':- module sample1.', '%(1-6)')}
_home = {}


def home_file(name):
    """HOME>NAME as the FEP gives it (fep.FileData), or None."""
    if name not in HOME_FILES:
        return None
    if name not in _home:
        import subprocess
        src, first, last, head, tail = HOME_FILES[name]
        text = subprocess.run(['uncompress', '-c', src], capture_output=True,
                              check=True).stdout.decode('ascii').split('\n')
        lines = text[first - 1:last]
        assert head in lines[0] and lines[-1].rstrip().endswith(tail), (lines[0], lines[-1])
        data = fepm.jis(''.join(x + '\n' for x in lines))
        _home[name] = fepm.FileData(
            data, 'PSI::%s>%s.1' % (HOME, name),
            fepm.attribute_string('pmpsi', 'pmpsi', '20-May-93', '00:00:00', '20-May-93',
                                  '00:00:00', 1, len(data), 0))
    return _home[name]


def home_listing(path):
    """--fep: 237's answer for the directory 204 opened (path 16-bit
    JIS, as kernel_file's), or None: the home directory's files
    (HOME_FILES), each with the version 221 gives it, ".1"
    (fep.listing; R7, ls, 2026-11-25, the form INFERENCE).  Any other
    directory: None, answered 5."""
    name = text_of(struct.unpack('>%dH' % (len(path) // 2), path))
    if name == HOME:
        return fepm.listing([n + '.1' for n in sorted(HOME_FILES)])
    return None


def kernel_file(path):
    """--fep: the file the kernel asks the FEP to open (the path is
    16-bit JIS, fep.ATTRIBUTES' Code 0): pimos:NAME from the held
    object/ set, HOME>NAME from HOME_FILES (home_file), None (abnormal)
    for a name either lacks and for me:; any other name raises, as any
    request fep.py does not know does."""
    name = text_of(struct.unpack('>%dH' % (len(path) // 2), path))
    if name.startswith('pimos:'):
        return held_object(name[len('pimos:'):])
    if name.startswith(HOME + '>'):
        return home_file(name[len(HOME) + 1:])
    if name.startswith('me:') or name.startswith('>sys>user>'):
        return None
    raise fepm.FepError('read_open of %r: no such file is served' % (name,))


def save_prompt(path, m, loaded, info):
    """--save-prompt FILE: the machine at the shell's prompt (run dry,
    no SCSI command moving, the window's getl held), with its device,
    for lockstep_shell.py.  The device's file server (a function of
    this module) is not pickled: lockstep_shell.py gives it back.
    Nor is its directory lister (R7 ls; 2026-11-25: pickled, it was
    __main__.home_listing, which lockstep_shell.py cannot load)."""
    dev = m.fep
    tr, m.tr = m.tr, None
    of, dev.open_file = dev.open_file, None
    ld, dev.list_dir = getattr(dev, 'list_dir', None), None
    lines, dev.script = dev.script, []
    info = dict(info, prompt=dict(instructions=tr.instructions, steps=m.steps,
                                  console=cons.console(tr)))
    with open(path, 'wb') as f:
        _pickler(f).dump((m, loaded, info))
    m.tr, dev.open_file, dev.script, dev.list_dir = tr, of, lines, ld
    say('saved the machine at the prompt (%d instructions) to %s' % (tr.instructions, path))


def go(m, loaded, info, bad, with_fep, lines=(), save_at=None):
    """top:go_pimos1(Loaded, BootInfo), run until the model refuses
    something.  with_fep: the device ref/pimm/fep.py is attached
    (Machine.fep, as ref_scsi.py attaches it), and when the machine
    has nothing left to run the commands that wait for the device are
    given it again (Machine.scsi_poll, as ref_scsi.boot does)."""
    im = m.im
    m.ahead = True
    boot_info = m.new_var()
    m.argv[1], m.argv[2] = pimm.marked(loaded), pimm.marked(boot_info)
    m.record(pimm.READY, pimm.predicate(im, 'top', 'go_pimos1/2'), m.argv[1:3])
    # BootInfo is made by the IPL's own make_boot_info/1, as ipl:boot0
    # makes it (docs/binary_reverse_engineering.md 1.3, item 11;
    # ref_scsi.py checks the string it gives): without it the
    # cluster of bios.kl1's create_os_device/3, element 0, is unbound
    # and scsi_fep:create/2@node(Cluster) cannot be placed
    m.spawn(pimm.predicate(im, 'ipl', 'make_boot_info/1'), [boot_info])
    m.tr = GoTrace()
    dev = None
    if with_fep:
        # getb counts 16-bit characters here (getb_unit 2, OURS,
        # 2026-11-24): the kernel's file device asks for Size*2+1
        # (server/fep/file/file_dvcb.kl1:301, 400), and a reply of an
        # odd number of bytes is widened with a zero byte at its end
        # (binary_reverse_engineering.md 1.4, "Widening"), so counted
        # in bytes every reply is odd and pimos.conf reached the
        # reader shifted by a byte after its first 1,471 bytes
        # (observed: with_console read, then end_of_file, the system/4
        # line lost).  Counted in characters every reply is even
        dev = m.fep = fepm.Fep(kernel_file, getb_unit=2, lines=lines, list_dir=home_listing)
    skips = 0
    try:
        while True:
            try:
                m.run(limit=10 ** 12)
                stop = 'nothing left to run, %d goals waiting' % m.nsusp
            except pimm.Suspend:
                stop = 'nothing left to run, %d goals waiting' % m.nsusp
            if dev is None:
                break
            if m.scsi_poll():
                skips = 0
                continue
            # R7L: an alarm armed (set_timer to a time still to come):
            # the clock moved on to it, and the next run's first goal
            # switch fires it -- after the device, before the FEP's
            # scripted events, as lockstep_shell.play (driver ALARM).
            # A machine that only ever re-arms is refused, not looped
            if m.alarm_var is not None:
                skips += 1
                if skips > 100:
                    raise pimm.Unimplemented('100 alarms in a row with nothing else to do')
                m.alarm_skip()
                continue
            skips = 0
            # PIMOS idles: the FEP's next scripted event, if a held
            # request waits for one (fep_services.md 7.5, 7.7 item 1)
            if save_at and 'getl' in dev.held.values() and \
                    (not dev.script or dev.script[0][0] == 'getl'):
                save_prompt(save_at, m, loaded, info)
                save_at = None
            if not dev.idle():
                break
            say('fep: a scripted event at %d instructions' % m.tr.instructions)
    except pimm.Unimplemented as e:
        stop = 'refused: %s' % e
    except pimm.Fail as e:
        stop = 'Fail %s' % e
    except fepm.FepError as e:
        stop = 'FepError: %s' % e
    shown = cons.console(m.tr)
    info['go'] = dict(instructions=m.tr.instructions, console=shown, stop=stop)
    if dev is not None:
        info['go']['fep'] = dict(commands=len(dev.wire), waiting=len(m.scsi_waiting),
                                 messages=dev.messages)
        for d, i, msg in dev.messages:
            say('fep %s device %d: %r' % (d, i, msg))
        for i, text in dev.log:
            say('fep text, device %d: %r' % (i, text))
        info['go']['fep']['held'] = dict(dev.held)
    say('go: %d instructions, console %r, stop %s' % (m.tr.instructions, shown, stop))
    if shown[:1] != [BANNER]:
        bad.append(('the console after go', shown))


def _pickler(f):
    """A pickler for the machine: its memory, code and registers are
    dict and list subclasses whose writes are traced through
    .machine, which a plain pickle sets only after their items."""
    # the rebuilders by an importable name, not __main__'s
    import longrun_ipl as here
    p = pickle.Pickler(f, protocol=5)
    p.dispatch_table = copyreg.dispatch_table.copy()
    p.dispatch_table[pimm._Mem] = lambda o: (here._mem, (dict.copy(o), o.machine))
    for c in (pimm._Code, pimm._Regs):
        p.dispatch_table[c] = lambda o: (here._seq, (type(o), list(o), o.__dict__))
    return p


def _mem(d, machine):
    x = pimm._Mem()
    dict.update(x, d)
    x.machine = machine
    return x


def _seq(cls, items, state):
    x = cls(items)
    x.__dict__.update(state)
    return x


def save(path, m, loaded, info):
    """--save FILE: the machine after the load and link (checked),
    the answer of load/4 and the counts, for --load."""
    tr, m.tr = m.tr, None
    with open(path, 'wb') as f:
        _pickler(f).dump((m, loaded, info))
    m.tr = tr
    say('saved the machine after the link to %s' % path)


def typed(argv):
    """The lines of every --type LINE, in order: what the operator
    types into the shell's window after the login (fep.py, OURS)."""
    return [argv[i + 1] for i, a in enumerate(argv) if a == '--type']


def main(argv):
    if '--load' in argv:
        # --load FILE --go [--fep]: from a machine --save wrote (its
        # checks passed when it was saved), straight to --go
        with open(argv[argv.index('--load') + 1], 'rb') as f:
            m, loaded, info = pickle.load(f)
        say('loaded the machine after the link')
        bad = []
        go(m, loaded, info, bad, '--fep' in argv, typed(argv),
           argv[argv.index('--save-prompt') + 1] if '--save-prompt' in argv else None)
        print('pimm longrun ipl --load: %s %r' % ('FAIL' if bad else 'PASS', info['go']))
        return 1 if bad else 0
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
    if '--save' in argv and not bad:
        save(argv[argv.index('--save') + 1], m, [w for _l, w in s.outs][-3], info)
    if '--go' in argv and '--reference' in argv and not bad:
        go(m, [w for _l, w in s.outs][-3], info, bad, '--fep' in argv, typed(argv))
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
