#!/usr/bin/env python3
"""The IPL's own file service, run on the reference model: PROTOTYPE.

    python3 ref/pimm/ref_scsi.py            every part but the real list
    python3 ref/pimm/ref_scsi.py --wire     and the first exchanges, in hex
    python3 ref/pimm/ref_scsi.py --real N   the held pimos.ipl, N commands

REFERENCE MODEL ONLY: there is no Bluespec side, no script, no
lockstep.  pimm.Machine is driven directly (not driver.Script: no
bench answer is needed any more, the IPL's requests are answered by
the device model ref/pimm/fep.py behind the built-ins scsi_init and
scsi_command).

What is run is the body of ipl:boot0/0 (asm/kl1decomp.py ipl; the
goals in the order its object code makes them, asm/kbndis.py ipl
boot0/0) without top:go/4:

    close(Close),
    ipl_loader:load(Files, OpenReqs, Close, Loaded),
    ipl_files(FileReq, "pimos:pimos.ipl", OpenReqs, Files),
    ipl_scsi:scsi(Fep, GeneralTail, FileReq, ScsiEnd),
    scsi_fep_module:create(0, 0, 7, 0, 1, 0, normal(Fep)),
    make_boot_info(BootInfo)

OURS, in place of top:go(Loaded, BootInfo, GeneralTail, ScsiEnd):
GeneralTail = 0 before anything runs (top:go/4's first body goal is
"C = 0"); nothing else of it (it starts a shoen).  boot/0's own shoen
is not there either: no priorities (load_files' @priority is dropped
as before), no exceptions.

Parts (all with a made-up pimos.ipl of OURS, the paths as the held
list spells them, >sys>csp>PIMOS.DIR>NAME):
  one file     pimm_patch_hash360E.sav.  Checked: the first commands
               on the bus against docs/binary_reverse_engineering.md
               1.3 (TEST UNIT READY, the 72-byte SEND of read_open,
               the RECEIVE and its 16-byte answer, the 24-byte getb),
               byte for byte; the requests of each device in order;
               Files; the console; Loaded = abnormal(["Undefined
               Module Found", "pool_usage"]), what lockstep_link.py
               gets with the test standing in for the file service;
               ScsiEnd = 0; Close = []; BootInfo; every device closed;
               no goal left waiting; the commands and heap cells
               pinned.
  two files    pimm_patch_hash360E.sav and pimm_patch_fepsv360E.sav
               (14,142 bytes: more than 7,936, so two replies).
               Loaded names fep_filter, as the bench-served loader
               does for that file (run once by hand through
               lockstep_link.one; not part of this test).
  characters   the same two, the device taking getb's 7936 as 16-bit
               characters (one reply of 14,142 bytes).  Same answer.
  late         the same two, the device refusing every RECEIVE once:
               the built-in's "not finished yet" path, completed by
               Machine.scsi_poll when the machine has run dry.  In
               every other part no command ever waits.
  odd          one file, 1001 bytes a getb.  Loaded =
               abnormal("internal error while reading unloaded
               file"): each reply is widened to 16 bits on its own
               and an odd one gets a zero byte at its end.
  small buffer one file, scsi_init reporting 512 bytes: the 2,604-byte
               reply is cut into continued packets (flag 1).  The IPL
               takes the first and STOPS: it issues no RECEIVE for
               the rest (scsi_fep_module:receive_packet2_1/9 goes
               back to the same request list).  Pinned as observed:
               Loaded unbound, one packet left in the device.

FOUND (docs/binary_reverse_engineering.md 1.4 "Run" has the detail):
the bytes 1.3 derived are right; the IPL does not determine the unit
of 7936 (the kernel source counts bytes, so that is the default
here); a getb reply must be an even number of bytes; a reply must
fit one packet; the loader asks twice more after end of data.

Observed fault injections, 2026-11-23, each into a COPY of this
directory (the tree itself was not edited):
  fep.py: a reply string's length word little-endian
        a reduction FAILS in builtin_utility:substring/5 (the run
        raises pimm.Fail) on the first reply with a string
  fep.py: a reply always carries device id 0
        every part: Loaded unbound, device 1 left open, 11 commands
  fep.py: TEST UNIT READY answered with status 2
        the IPL sends REQUEST SENSE (CDB 0300000008, 8 bytes in),
        which the device refuses (FepError)
  pimm.py scsi_do: Data is the bytes received, not the whole buffer
        Unimplemented at the next RECEIVE (length over the buffer)
  pimm.py change_element_size: 8 to 16 with the low byte first
        the path of the first .sav open is not JIS (this bench's
        KeyError)
  pimm.py scsi_do: TransferredLength is the buffer's length
        caught ONLY by the pinned heap cells (458,899 for 388,311 in
        "one file"); Files and Loaded are the same.  The IPL cuts a
        reply by its own length words
  pimm.py: a merger input bound to a vector refused (as before)
        Unimplemented in the first part: the path is run
  pimm.py: string_operation not waiting for its vector's element
        Unimplemented (an unbound element reaches the operation)
  pimm.py: read_eagerly stopping when a variable is noted
        it stops in the first part: `alternatively` is met with a
        variable noted, where `otherwise` would suspend
  pimm.py: not_equal as equal
        every part: 5 commands, only the list opened, Loaded unbound
  pimm.py: b_modulo one too many
        the device refuses the first SEND (66 bytes for 64)
  pimm.py: b_string's length one too many
        Unimplemented (string_operation's bounds)
  pimm.py: enqueue_goal_to_processor refusing processor 0;
           put_reused_structure without the long vector's descriptor
        Unimplemented at once, both
NOT caught:
  - fep.py padding a reply's string to 2 bytes, not 4, and pimm.py
    b_divide one too many (four are run): both only place what
    follows a string, and the string is the last thing in every
    reply the IPL gets here;
  - scsi_command not waiting for its vector's elements: they were
    bound every time (the wait is NOT run).
Not run at all: wait_vector_1.

Not run: top:go/4 and the shoens; an open that fails; a read error;
abort (70); attention (status 3); a message the IPL sends in more
than one packet; REQUEST SENSE; more than one processor.
"""
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import pimm  # noqa: E402
import fep as fepm  # noqa: E402
import lockstep_cons as cons  # noqa: E402
import lockstep_file as lfile  # noqa: E402
import lockstep_ipll as ipll  # noqa: E402
import lockstep_link as link  # noqa: E402

LIST = 'pimos:pimos.ipl'
DIR = '>sys>csp>PIMOS.DIR>'
HASH, FEPSV = 'pimm_patch_hash360E.sav', 'pimm_patch_fepsv360E.sav'

# docs/binary_reverse_engineering.md 1.3, items 7 and 8, as the
# document derived them before anything was run
DOC = dict(
    tur='0000000000',
    open_cdb='0a00000048',
    open=('00000000 00000000 000000c9 00000004 00000000 ffffffff ffffffff 0000001e '
          '00000000 00000000 2370 2369 236d 236f 2373 2127 2370 2369 236d 236f 2373 2125 '
          '2369 2370 236c 0000'),
    receive_cdb='0820%06x' % fepm.Fep.MAX_BUFFER,
    open_reply='00000000 00000000 00000001 00000000',
    getb_cdb='0a00000018',
    getb='00000000 00000000 000000d2 00000001 ffffffff 00001f00')

# (label, files, device options)
PARTS = [('one file', [HASH], {}),
         ('two files', [HASH, FEPSV], {}),
         ('characters', [HASH, FEPSV], dict(getb_unit=2)),
         ('late', [HASH, FEPSV], dict(lag=True)),
         ('odd', [HASH], dict(getb_bytes=1001)),
         ('small buffer', [HASH], dict(max_buffer=512))]
# part "odd", as observed 2026-11-23: the loader's answer
ODD = ('abnormal', (8, [ord(c) for c in 'internal error while reading unloaded file']))
# pinned, as observed 2026-11-23: (commands on the bus, heap cells)
PINNED = {'one file': (19, 388311), 'two files': (31, 684498), 'characters': (29, 664477),
          'late': (31, 684648), 'odd': (21, 218326), 'small buffer': (13, 35968)}


FILES = {}          # the .sav files read so far, by path


class Console(list):
    """A trace that keeps what the console is given and nothing else."""

    def append(self, line):
        if line[0] in 'CS':
            list.append(self, line)


def words_bytes(words):
    return struct.pack('>%dH' % len(words), *words)


def listing(files):
    """A pimos.ipl of ours: a full path a line."""
    out = []
    for f in files:
        out += cons.jis(DIR + f) + [10]
    return words_bytes(out)


def unresolved(files):
    """The modules the files name and do not hold: lockstep_link's
    reading (the modules called) and those named as a module constant
    (asm/unlsav.py's 'module' entries, which lockstep_link.unresolved
    does not count: pimm_patch_fepsv360E.sav names fep_filter so)."""
    have, want = set(), list(link.unresolved(files))
    for f in files:
        have |= {m['name'] for m in link.modc.modules(f)}
    for f in files:
        for a in link.gca.areas(f):
            for top in a[3]:
                if top[0] == 'module' and top[1][1] not in have:
                    want.append(top[1][1].replace('2', '_'))
    return want


def boot(list_bytes, steps=200000000, **device):
    """Run boot0's body (see the header).  Returns the machine, its
    variables by name, the names the device was asked to open."""
    m = pimm.Machine()
    m.tr = Console()
    im = m.im
    names = {name: n for n, name in im.sym.items()}
    opened = []

    def open_file(path):
        name = cons.ascii_of(struct.unpack('>%dH' % (len(path) // 2), path))
        opened.append(name)
        if name == LIST:
            return list_bytes
        if name.startswith(DIR):
            if name not in FILES:
                FILES[name] = words_bytes(lfile.file_words(name[len(DIR):]))
            return FILES[name]
        return None
    m.fep = fepm.Fep(open_file, **device)
    v = {k: m.new_var() for k in ('Fep', 'GeneralTail', 'FileReq', 'ScsiEnd', 'OpenReqs',
                                  'Files', 'Close', 'Loaded', 'BootInfo')}
    P = lambda mod, p: pimm.predicate(im, mod, p)       # noqa: E731
    I = lambda n: (pimm.INT, n)                          # noqa: E731
    m.unify(v['GeneralTail'], I(0))                      # for top:go/4: ours
    m.spawn(P('ipl', 'close/1'), [v['Close']])
    m.spawn(P('ipl_loader', 'load/4'), [v['Files'], v['OpenReqs'], v['Close'], v['Loaded']])
    m.spawn(P('ipl', 'ipl_files/4'), [v['FileReq'], m.make_string(16, cons.jis(LIST)),
                                      v['OpenReqs'], v['Files']])
    m.spawn(P('ipl_scsi', 'scsi/4'), [v['Fep'], v['GeneralTail'], v['FileReq'], v['ScsiEnd']])
    w, a = m.vnew(2)
    m.mem[a] = (pimm.ATOM, names['normal'])
    m.mem[a + 1] = v['Fep']
    m.spawn(P('scsi_fep_module', 'create/7'), [I(0), I(0), I(7), I(0), I(1), I(0), w])
    m.spawn(P('ipl', 'make_boot_info/1'), [v['BootInfo']])
    t = time.time()
    m.polls = 0
    while True:
        try:
            m.run(limit=steps)
        except pimm.Suspend:
            pass
        # the machine has nothing to run: has the device anything for
        # a command that waits?
        if not m.scsi_poll():
            break
        m.polls += 1
    m.seconds = time.time() - t
    return m, v, opened


def check(label, files, device, m, v, opened):
    bad = []
    f = m.fep
    T = lambda k: None if m.unbound(m.deref(v[k])) else m.term(v[k])   # noqa: E731
    paths = [DIR + x for x in files]
    if opened != [LIST] + paths:
        bad.append(('opened', opened))
    if T('Files') != [(16, cons.jis(p)) for p in paths]:
        bad.append(('Files', T('Files')))
    loaded = T('Loaded')
    if label == 'small buffer':
        # the IPL stops: see the header
        last = f.wire[-1]
        if not (loaded is None and len(f.replies) == 1 and last[0] == 'RECEIVE'
                and last[3][4:8] == b'\0\0\0\1' and len(last[3]) == 512 and m.nsusp
                and PINNED[label] == (len(f.wire), m.hp - m.load - pimm.HEAP)):
            bad.append(('stopped', loaded, len(f.replies), last[0], m.nsusp, len(f.wire),
                        m.hp - m.load - pimm.HEAP))
        return bad
    if label == 'odd':
        if loaded != ODD:
            bad.append(('Loaded', str(loaded)[:200]))
    else:
        msg = (8, [ord(c) for c in 'Undefined Module Found'])
        missing = [(16, cons.jis(n)) for n in unresolved(files)]
        if not (isinstance(loaded, tuple) and loaded[0] == 'abnormal' and len(loaded[1]) == 2
                and loaded[1][0] == msg and loaded[1][1] in missing):
            bad.append(('Loaded', str(loaded)[:200]))
        got = cons.console(m.tr)
        if got != ['IPL loading'] + paths + ['Link Modules ...']:
            bad.append(('console', got))
    if T('ScsiEnd') != 0 or T('Close') != []:
        bad.append(('ScsiEnd, Close', T('ScsiEnd'), T('Close')))
    info = [0, 0, 7, 0, 1] + [0] * 11 + [len(LIST)] + cons.jis(LIST)
    if T('BootInfo') != (16, info):
        bad.append(('BootInfo', T('BootInfo')))
    if f.files or f.replies or f.partial or m.scsi_waiting:
        bad.append(('device left', sorted(f.files), len(f.replies), len(m.scsi_waiting)))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    # the requests, per device: open, getb to the end of data, close
    for dev in range(len(files) + 1):
        seq = [(d, msg[0]) for d, i, msg in f.messages if i == dev]
        n = sum(1 for d, c in seq if (d, c) == ('>', fepm.GETB))
        want = [('>', fepm.READ_OPEN), ('<', fepm.NORMAL)]
        # the list is asked for once more after the end of data, a
        # .sav file twice more (observed: the loader asks again)
        ends = 1 if dev == 0 else 2
        want += [('>', fepm.GETB), ('<', fepm.NORMAL)] * (n - ends)
        want += [('>', fepm.GETB), ('<', fepm.EOD)] * ends
        want += [('>', fepm.CLOSE), ('<', fepm.NORMAL)]
        if seq != want and label != 'odd':
            bad.append(('device %d' % dev, seq))
    getb = [msg for d, i, msg in f.messages if d == '>' and msg[0] == fepm.GETB]
    if any(msg != [fepm.GETB, 7936] for msg in getb):
        bad.append(('getb', getb[:3]))
    if label == 'one file':
        bad += against_document(f.wire)
    if (label == 'late') != bool(m.polls) or (label == 'late') != bool(m.scsi_deferred):
        bad.append(('commands that waited', m.scsi_deferred, m.polls))
    got = (len(f.wire), m.hp - m.load - pimm.HEAP)
    if PINNED.get(label) != got:
        bad.append(('counts', got))
    return bad


def against_document(wire):
    """The first four commands on the bus against 1.3."""
    H = lambda t: bytes.fromhex(t.replace(' ', ''))     # noqa: E731
    want = [('TEST UNIT READY', H(DOC['tur']), b'', b''),
            ('SEND', H(DOC['open_cdb']), H(DOC['open']), b''),
            ('RECEIVE', H(DOC['receive_cdb']), b'', H(DOC['open_reply'])),
            ('SEND', H(DOC['getb_cdb']), H(DOC['getb']), b'')]
    if len(wire) < len(want):
        return [('the bus: %d commands' % len(wire),)]
    return [('the bus, command %d' % i, w[0], w[1].hex(), fepm.hexdump(w[2] + w[3]))
            for i, (w, x) in enumerate(zip(wire, want)) if w != x]


def show_wire(wire, n):
    for name, cdb, out, back in wire[:n]:
        data = out or back
        print('  %-15s CDB %s  %d bytes %s' % (name, cdb.hex(), len(data),
                                                 'out' if out else 'in' if back else ''))
        for i in range(0, min(len(data), 128), 32):
            print('      ' + fepm.hexdump(data[i:i + 32]))
        if len(data) > 128:
            print('      ...')


def text(t):
    """A term for a message: strings as text."""
    if isinstance(t, tuple) and len(t) == 2 and t[0] in (8, 16) and isinstance(t[1], list):
        return '"%s"' % (''.join(map(chr, t[1])) if t[0] == 8 else cons.ascii_of(t[1]))
    if isinstance(t, tuple):
        return '%s(%s)' % (t[0], ', '.join(text(x) for x in t[1:]))
    if isinstance(t, list):
        return '[%s]' % ', '.join(text(x) for x in t)
    return '(unbound)' if t is None else str(t)


def real(limit):
    """The held pimos.ipl, until the device has taken `limit` commands."""
    words = ipll.list_words()
    m, v, opened = boot(words_bytes(words), limit=limit)
    f = m.fep
    print('the held pimos.ipl, %d commands: opened %r' % (len(f.wire), opened))
    files = None if m.unbound(m.deref(v['Files'])) else m.term(v['Files'])
    print('  Files: %d names, the held list has %d: %s'
          % (len(files or []), len(ipll.by_hand(words)),
             files == [(16, list(x)) for x in ipll.by_hand(words)]))
    print('  console %r' % (cons.console(m.tr),))
    per = {}
    for d, i, msg in f.messages:
        if d == '<' and msg[0] == fepm.NORMAL and len(msg) == 2:
            per[i] = per.get(i, 0) + len(msg[1])
    print('  bytes given per device %r' % (per,))
    print('  heap %d cells, %d instructions, %.0f s' % (m.hp - m.load - pimm.HEAP, m.steps,
                                                       m.seconds))
    return 0


def main(argv):
    if '--real' in argv:
        return real(int(argv[argv.index('--real') + 1]))
    bad = []
    for label, files, device in PARTS:
        m, v, opened = boot(listing(files), **device)
        b = check(label, files, device, m, v, opened)
        bad += [(label,) + x for x in b]
        loaded = text(m.term(v['Loaded']))
        print('%-12s %3d commands, %d getb, %8d heap cells, %8d instructions, %4.1f s, '
              'Loaded = %s'
              % (label, len(m.fep.wire),
                 sum(1 for d, i, x in m.fep.messages if d == '>' and x[0] == fepm.GETB),
                 m.hp - m.load - pimm.HEAP, m.steps, m.seconds, loaded))
        if '--wire' in argv and label == 'one file':
            show_wire(m.fep.wire, 12)
    if bad:
        print('ref scsi: FAIL %r' % (bad[:4],))
        return 1
    print("ref scsi: PASS (the body of ipl:boot0 without top:go, on the reference model "
          "alone: the IPL's own SCSI file service against ref/pimm/fep.py; the first "
          'commands on the bus are those of docs/binary_reverse_engineering.md 1.3, byte '
          'for byte; %d parts)' % len(PARTS))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
