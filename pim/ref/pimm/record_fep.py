#!/usr/bin/env python3
"""Record the SCSI commands the IPL gives the FEP, as tapes for the
Bluespec FEP emulator's bench (bsv/PimmFepEmuTb.bsv, bsv/run_fepemu.sh).

    python3 ref/pimm/record_fep.py            record every part (slow: it
                                              runs ref_scsi.py's parts, ~3 min)
    python3 ref/pimm/record_fep.py --part odd one part
    python3 ref/pimm/record_fep.py --check    the tapes on disk are what a
                                              recording gives now
    python3 ref/pimm/record_fep.py --kernel PKL [--check]
                                              the "kernel" tape only, from
                                              PIMOS's start (PKL: a machine
                                              longrun_ipl.py --reference
                                              --save wrote; seconds)

ALL OURS (a test tool).  What a tape holds: the device options of the
part and every call the reference model made of Fep.command, in order,
INCLUDING the calls answered None (a RECEIVE with nothing queued, the
"late" part's refusals) and the retries Machine.scsi_poll makes.  It
holds the commands only, never the device's answers: those are made at
test time by replaying the commands into a fresh ref/pimm/fep.py
(bsv/fepemu_check.py), so fep.py itself stays the oracle.  SEND data is
kept (direction 1); a RECEIVE's data argument is the buffer the IPL
handed the built-in (pimm.py scsi_do), which fep.py ignores, so it is
not kept.

How it records without changing fep.py's behaviour: ref_scsi.boot makes
its device as `fepm.Fep(open_file, **device)`, looked up at call time,
so fepm.Fep is replaced for the run by a subclass whose command()
notes its arguments and returns what fep.py's command() returned.
The part is then checked by ref_scsi.check as ref_scsi.py checks it
(and PINNED), and the recorded commands are replayed into a fresh
fep.Fep and must give the same answers as the run gave: so a tape is
known to be the run, not a reconstruction.

Parts: ref_scsi.PARTS (one file, two files, characters, late, odd,
small buffer), and "direct": a short sequence of OURS driven straight
into fep.Fep (no machine), for what the IPL's parts never do: an open
of a file that is not there (status 5), abort (70), a request in two
continued packets, RECEIVEs small enough to cut a reply three times,
two devices open at once, and each FepError (another unit, another LUN
in the CDB, an unknown CDB, getb on a device not open, a second open,
close not open, a packet flag 2).  An error ends fep.py's use (the
caller raises); the tape starts a new section ("config" again) after
each.

Besides commands a tape holds (2026-11-24): `ticks N`, the clock set
into Fep.ticks before the commands after it (pimm.py scsi_do sets it
before every command; written only where it changes, a fresh Fep's
being 0), which get_date_time's answer follows; `idle`, a call of
Fep.idle(), the event longrun_ipl.go asks for when the machine has run
dry (its answer, True if a held request was answered, is compared like
a command's); `files pimos:` for a tape whose files are the kernel's
(longrun_ipl.kernel_file: the held object directory as pimos:NAME);
and `script login getl=TEXT ...`, events in place of fep.py's own
script (direct kernel only).

"direct kernel": a direct sequence of OURS (no machine) for the
answers fep.py has for PIMOS's start, and their edges: INQUIRY to unit
7 (and while a reply is queued, and under lag: it is not a RECEIVE),
TEST UNIT READY to each absent unit 0-5 (Result NO_DEVICE, also with a
LUN and CDB bytes fep.py does not look at), append_open (203) with the
kernel's own message, with an integer path, then read_open, getb and
close on the appending device, its close again (the appending one,
2026-11-24) and append_open after it; and as one section each, every FepError
nearby: INQUIRY of another length, LUN or direction, or to an absent
unit; TEST UNIT READY to unit 6, to an absent unit with a direction,
length or CDB length; append_open twice, on a device with a file open,
with three arguments; getb and putb (111) on a device that only
appends, close twice and close with an argument.  Then (direct_login_sections) the answers from fep_attributes
(240) to the shell's prompt: 240 (and cut), the timer with the clock
at 0, a millisecond before midnight, midnight, the top of 48 bits; the
files pimos: has and has not, me: and the home; the replier, the local
and tcpip servers (a name with '_' as row 23 and an odd last byte), the
user device (cut; its data 0 to 4+2n bytes long), a window and its
calls (one with six arguments), getl held; the events of the tape's
script (two logins, two lines): the lowest device first, an event that
waits for its hold, abort of a held request [6], a hold that outlives
its window's close, devices that are a file and a timer or a window and
a timer at once (fep.py's order of tests); the event under lag and
after a refusal; and every FepError (or Python error) next to them.
Then (2026-11-24, fep.py's answers for a typed shutdown) the string-I/O
window pimos_standard_io_window: 104, 130, 141, 111 (and cut), getl
held and answered by the event, close; {-1, 80} twice (no reply); and
the FepErrors next to them (an integer putb text, io 112 and 127, a
string command, io while held, a window's own putb, another name, 80
on device 5, 80 with an argument).

"kernel": recorded from the real PIMOS start, `longrun_ipl.go` on a
machine `longrun_ipl.py --reference --save PKL` wrote, with
fepm.Fep replaced as above (go() makes its device as fepm.Fep at call
time).  Not made by a plain run (it needs PKL, ~1.1 GB, 15-50 min to
make); `--kernel PKL --type shutdown --type yes --check` checks it
(--type LINE: longrun_ipl.py's typed lines; the tape's script is then
fep.py's for those lines).  Its last commands move as
PIMOS's start goes further (the stop is another agent's work): its
check is that the replay gives the run's answers and that the first
ten answered commands are the conversation of
docs/binary_reverse_engineering.md 1.4 (TEST UNIT READY and INQUIRY
to unit 7, TEST UNIT READY to 5..0, the append_open SEND, its RECEIVE).
The device's options are the run's (getb_unit 2), its clock and its
events are on the tape, and it prints what the emulator's limits of
OURS must hold.  Recorded 2026-11-24 to the shell's prompt (a cached
machine; 50 s): 8,586,110 instructions, 175 calls (126
answered, 49 not ready), 2 events (the login answered; then nothing
to answer), the stop "nothing left to run, 1,220 goals waiting" with
the login server's io(1) and the window's getl held.
Re-recorded 2026-11-24 after the merger change (docs/pimm_semantics.md
merge; machine saved under it, heap 73,594,186 cells): to the prompt
8,587,092 instructions, 178 calls (127 answered); and then, the tape
on disk, to PIMOS END with --type shutdown --type yes: 8,766,339
instructions, 220 calls (155 answered, 65 not ready), 4 events (3
answered: the login, "shutdown", "yes"), the console ending "PIMOS
END********", {-1, 80} received, nothing held, the stop "nothing left
to run, 253 goals waiting"; most at once: 4 replies queued, 2 files,
1 appending, 1 timer, 3 string-I/O, 1 window, 2 held; the largest
request 88 bytes.
Re-recorded 2026-11-24 with the login record's ID 0 (fep.py LOGIN, read
from pimfep's get_key/4; it was 1, OURS): the same 220 calls, 155
answered, 4 events; the three replier texts' element 0 is 0000 for
0001; 8,766,319 instructions to PIMOS END (20 fewer), the prompt at
8,587,072.
"""
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TAPES = os.path.join(HERE, 'fep_tapes')

import ref_scsi as rs  # noqa: E402
import fep as fepm  # noqa: E402

ORIGINAL = fepm.Fep
SLUG = {'one file': 'one_file', 'two files': 'two_files', 'characters': 'characters',
        'late': 'late', 'odd': 'odd', 'small buffer': 'small_buffer', 'direct': 'direct',
        'direct kernel': 'direct_kernel', 'kernel': 'kernel'}


class Recording(ORIGINAL):
    """fep.Fep, noting each call and its answer, the clock it was given
    before each command (Fep.ticks, which get_date_time's answer
    follows), each Fep.idle() and its answer, and the device made (its
    options)."""
    calls = None
    made = None

    def __init__(self, open_file, **kw):
        ORIGINAL.__init__(self, open_file, **kw)
        Recording.made = self

    def command(self, unit, lun, cdb, length, direction, data):
        got = ORIGINAL.command(self, unit, lun, cdb, length, direction, data)
        Recording.calls.append(((unit, lun, bytes(cdb), length, direction,
                                 bytes(data) if direction == 1 else b''), got, self.ticks))
        return got

    def idle(self):
        got = ORIGINAL.idle(self)
        Recording.calls.append((IDLE, got, self.ticks))
        return got


# A tape's two marks besides a command (OURS): ('ticks', N) sets
# Fep.ticks, the clock the reference model gives the device before each
# command (pimm.py scsi_do), written only when it changes (a fresh Fep's
# is 0); IDLE is a call of Fep.idle(), the bench's question when the
# machine has run dry (longrun_ipl.go), answered True if it queued a
# reply (a held request answered by the next scripted event)
IDLE = ('idle',)
# the `files` of a tape whose files are the kernel's: pimos:NAME from the
# held object directory (longrun_ipl.kernel_file), not ref_scsi.py's
OBJECTS = 'pimos:'


def is_command(c):
    return len(c) == 6


def tape_of(calls):
    """Recording.calls as a section's items (the commands, ('ticks', N)
    where the clock changed, IDLE) and the answers seen, as replay()
    gives them."""
    items, seen, ticks = [], [], 0
    for c, got, t in calls:
        if t != ticks:
            items.append(('ticks', t))
            ticks = t
        items.append(c)
        if c == IDLE:
            seen.append(('I', bool(got)))
        else:
            seen.append(('N',) if got is None else ('D', got[0], bytes(got[1])))
    return items, seen


def options(device):
    return dict(getb_unit=device.get('getb_unit', 1), getb_bytes=device.get('getb_bytes') or 0,
                lag=int(bool(device.get('lag'))),
                max_buffer=device.get('max_buffer') or ORIGINAL.MAX_BUFFER)


def device_kwargs(opts):
    return dict(getb_unit=opts['getb_unit'], getb_bytes=opts['getb_bytes'] or None,
                lag=bool(opts['lag']), max_buffer=opts['max_buffer'])


def open_file_for(files):
    """ref_scsi.boot's open_file, outside a machine: the list of OURS
    and the held .sav files, by the path's bytes; for files [OBJECTS],
    the kernel's (longrun_ipl.kernel_file)."""
    if files == [OBJECTS]:
        import longrun_ipl as lr
        return lr.kernel_file
    lst = rs.listing(files)

    def open_file(path):
        name = rs.cons.ascii_of(struct.unpack('>%dH' % (len(path) // 2), path))
        if name == rs.LIST:
            return lst
        if name.startswith(rs.DIR):
            if name not in rs.FILES:
                try:
                    rs.FILES[name] = rs.words_bytes(rs.lfile.file_words(name[len(rs.DIR):]))
                except UnboundLocalError:
                    # ref_scsi.py's open_file raises here (lockstep_file.file_words
                    # finds no member); fep.py's contract is "open_file -> the
                    # file's bytes, or None", so a name not held is None
                    return None
            return rs.FILES[name]
        return None
    return open_file


def replay(sections, files, script=None):
    """Each section's commands into a fresh fep.Fep: the answers, an
    answer being ('D', result, bytes), ('N',) or ('E', message); after
    an E the rest of the section is E too (fep.py's caller has raised);
    ('I', queued) for an IDLE.  A ('ticks', N) sets the clock and has
    no answer.  script: the events in place of fep.py's own (a tape's
    `script` line), or None."""
    out = []
    for opts, cmds in sections:
        f = ORIGINAL(open_file_for(files), **device_kwargs(opts))
        if script is not None:
            f.script = list(script)
        dead = None
        for c in cmds:
            if c[0] == 'ticks':
                f.ticks = c[1]
                continue
            if dead is not None:
                out.append(('E', 'after: ' + dead))
                continue
            if c == IDLE:
                out.append(('I', bool(f.idle())))
                continue
            unit, lun, cdb, length, direction, data = c
            try:
                got = f.command(unit, lun, cdb, length, direction, data)
            except Exception as e:          # FepError, or Python's own on a bad argument
                dead = '%s: %s' % (type(e).__name__, e)
                out.append(('E', dead))
                continue
            out.append(('N',) if got is None else ('D', got[0], bytes(got[1])))
    return out


# ---- the direct section, OURS ----------------------------------------
def pkt(dev, flag, body):
    return struct.pack('>ii', dev, flag) + body


def cdb(op, lun, n):
    return bytes([op, lun << 5, n >> 16 & 255, n >> 8 & 255, n & 255])


def send(p, lun=0, unit=7):
    return (unit, lun, cdb(fepm.SEND, lun, len(p)), len(p), 1, p)


def receive(n):
    return (7, 1, cdb(fepm.RECEIVE, 1, n), n, 2, b'')


def jis(text):
    return rs.words_bytes(rs.cons.jis(text))


def open_msg(path):
    return fepm.pack_message([fepm.READ_OPEN, b'', 0, 0, jis(path)])


def direct_sections():
    H = rs.DIR + rs.HASH
    tur = (7, 0, bytes(5), 0, 0, b'')
    getb = lambda n: fepm.pack_message([fepm.GETB, n])         # noqa: E731
    close = fepm.pack_message([fepm.CLOSE])
    body = open_msg(rs.LIST)
    std = dict(getb_unit=1, getb_bytes=0, lag=0, max_buffer=16000)
    s = []
    # 1. a missing file; a prefix and an extension of a held name (not
    # the card's decoys, which are one character off: so a lookup that is
    # not exact answers from a decoy here or in the parts); abort; two
    # devices; a request in two packets; small RECEIVEs; EOD twice
    s.append((std, [
        tur, receive(64),                                   # nothing queued: None
        send(pkt(3, 0, open_msg('pimos:nothing.ipl'))), receive(64),           # status 5
        send(pkt(4, 0, open_msg(rs.LIST[:-3]))), receive(64),                  # prefix: 5
        send(pkt(5, 0, open_msg(H + 'yy'))), receive(64),                      # extension: 5
        send(pkt(1, 0, fepm.pack_message([fepm.ABORT]))), receive(64),         # no reply
        send(pkt(2, 1, body[:20])), send(pkt(2, 0, body[20:])),               # continued
        send(pkt(6, 0, open_msg(H))),
        receive(64), receive(64),
        send(pkt(2, 0, getb(37))), send(pkt(6, 0, getb(100))),
        receive(20), receive(20), receive(20), receive(9), receive(200),
        receive(16000),
        send(pkt(6, 0, getb(1 << 20))), receive(16000), receive(16000), receive(16000),
        send(pkt(6, 0, getb(7936))), receive(8000),
        send(pkt(2, 0, getb(7936))), receive(8000),
        send(pkt(2, 0, getb(7936))), receive(8000),
        send(pkt(2, 0, close)), send(pkt(6, 0, close)), receive(64), receive(64),
        receive(64)]))
    # 2. each FepError, one a section
    errs = [
        [(6, 0, bytes(5), 0, 0, b'')],                      # another unit
        [(7, 0, bytes([0, 0x20, 0, 0, 0]), 0, 0, b'')],      # the CDB's LUN not the LUN
        [(7, 0, bytes([3, 0, 0, 0, 8]), 8, 2, b'')],         # REQUEST SENSE
        [send(pkt(0, 0, getb(10)))],                         # getb, nothing open
        [send(pkt(0, 0, body)), send(pkt(0, 0, body))],     # open twice
        [send(pkt(0, 0, close))],                            # close, nothing open
        [send(pkt(0, 2, body))],                             # flag 2
        [send(pkt(0, 0, body)[:6])],                         # a packet of 6 bytes
        [send(pkt(0, 0, body + bytes(4)))],                  # 4 bytes left over
        [tur, (7, 0, cdb(fepm.SEND, 0, 10), 12, 1, bytes(12))],   # CDB length not length
    ]
    for e in errs:
        s.append((std, e))
    # 3. the device options of the parts, each on a short open-getb
    for opts in (dict(std, getb_unit=2), dict(std, getb_bytes=11), dict(std, lag=1)):
        s.append((opts, [send(pkt(9, 0, open_msg(H))), receive(64), receive(64),
                         send(pkt(9, 0, getb(5))), receive(64), receive(64), receive(64)]))
    return s


# ---- the direct kernel section, OURS ---------------------------------
def inquiry(n=255, lun=0, unit=7, direction=2, clen=None):
    c = bytes([fepm.INQUIRY, lun << 5, 0, 0, n if clen is None else clen])
    return (unit, lun, c, n, direction, b'')


def tur_at(unit, lun=0, c=bytes(5), length=0, direction=0):
    return (unit, lun, c, length, direction, b'')


def append_msg(path):
    return fepm.pack_message([fepm.APPEND_OPEN, b'', 0, 0, path])


def direct_kernel_sections():
    std = dict(getb_unit=1, getb_bytes=0, lag=0, max_buffer=16000)
    syslog = jis('pimos:pimos.syslog')
    getb = lambda n: fepm.pack_message([fepm.GETB, n])         # noqa: E731
    close = fepm.pack_message([fepm.CLOSE])
    s = []
    # 1. the kernel's bus scan and its first message, then the edges
    # that are answered
    s.append((std, [
        tur_at(7), inquiry()] + [tur_at(u) for u in (5, 4, 3, 2, 1, 0)] + [
        tur_at(3, lun=2, c=bytes([0, 0x40, 0, 0, 9])),        # LUN, CDB bytes: not looked at
        tur_at(0, lun=1, c=bytes([0, 0x1f, 1, 2, 3])),
        send(pkt(16, 0, append_msg(syslog))),
        inquiry(),                                          # a reply queued: INQUIRY answers
        receive(16384), receive(16384),                     # the reply; then nothing
        send(pkt(17, 0, fepm.pack_message([fepm.APPEND_OPEN, b'', 0, 0, 5]))),  # an integer path
        receive(64),
        send(pkt(16, 0, open_msg(rs.LIST))), receive(64),   # read_open on an appending device
        send(pkt(16, 0, getb(40))), receive(200), send(pkt(16, 0, close)), receive(64),
        tur_at(5), inquiry(),
        # the close of the append-opened file (2026-11-24: fep.py answers
        # it [1], the syslog's at PIMOS's end): a file closed twice on one
        # device (the read file first, then the appending), and the
        # device appends again after it
        send(pkt(16, 0, close)), receive(64),
        send(pkt(20, 0, append_msg(syslog))), receive(64),
        send(pkt(20, 0, close)), receive(64),
        send(pkt(20, 0, append_msg(syslog))), receive(64)]))
    # 2. lag: INQUIRY is not held back
    s.append((dict(std, lag=1), [
        send(pkt(16, 0, append_msg(syslog))), inquiry(), receive(64), inquiry(), receive(64)]))
    # 3. an odd-length path (read_open would raise; append_open does not look)
    s.append((std, [send(pkt(16, 0, append_msg(b'abc'))), receive(64)]))
    # 4. each FepError, one a section
    errs = [
        [inquiry(36)],                                      # another length
        [inquiry(255, clen=254)],                           # the CDB's length not the length
        [inquiry(lun=1)],                                   # LUN 1
        [inquiry(direction=0)],                             # no data in
        [inquiry(unit=3)],                                  # INQUIRY to an absent unit
        [tur_at(6)],                                        # PIM/m's own unit
        [tur_at(0xffffffff)],                               # unit -1 (not absent: not 0..5)
        [tur_at(2, direction=2)],                           # absent, a direction
        [tur_at(2, length=4)],                              # absent, a length
        [tur_at(2, c=bytes(6))],                            # absent, a 6-byte CDB
        [send(pkt(16, 0, append_msg(syslog))), send(pkt(16, 0, append_msg(syslog)))],  # twice
        [send(pkt(16, 0, open_msg(rs.LIST))), send(pkt(16, 0, append_msg(syslog)))],   # file open
        [send(pkt(16, 0, fepm.pack_message([fepm.APPEND_OPEN, b'', 0, syslog])))],     # 3 args
        [send(pkt(16, 0, append_msg(syslog))), send(pkt(16, 0, getb(10)))],            # getb
        [send(pkt(16, 0, append_msg(syslog))), send(pkt(16, 0, close)),
         send(pkt(16, 0, close))],                                                     # close twice
        [send(pkt(16, 0, append_msg(syslog))),
         send(pkt(16, 0, fepm.pack_message([fepm.CLOSE, 0])))],                        # close, an argument
        [send(pkt(16, 0, append_msg(syslog))),
         send(pkt(16, 0, fepm.pack_message([111, b'log line'])))],                     # putb
    ]
    for e in errs:
        s.append((std, e))
    return s + direct_login_sections(std)


# the script of the direct kernel tape (its `script` line), in place of
# fep.py's one login: two logins and two lines, so that the order of the
# events, the lowest device first and an event that waits are tried
# (OURS: both logins carry fep.LOGIN's ID 0, where the PSI's rule,
# fep_services.md 6.5, would give the second 1)
DIRECT_KERNEL_SCRIPT = [('login', fepm.LOGIN), ('getl', 'dir'), ('login', fepm.LOGIN),
                        ('getl', 'x')]


def direct_login_sections(std):
    """The answers fep.py has from 240 on (docs/fep_services.md 6, 7),
    their edges, and every FepError next to them (OURS, 2026-11-24)."""
    m = lambda *a: fepm.pack_message(list(a))                   # noqa: E731
    sd = lambda dev, *a: send(pkt(dev, 0, m(*a)))               # noqa: E731
    fj = fepm.jis
    strio = lambda dev, name: sd(dev, fepm.CREATE_STRING_IO, b'', 0, 0, fj(name))  # noqa: E731
    io = lambda dev, c, data: sd(dev, fepm.IO, c, data)         # noqa: E731
    window = lambda dev: sd(dev, fepm.CREATE_WINDOW, b'', fj('pmpsi'), b'')  # noqa: E731
    r = receive(64)
    day = 16 * 86400000
    # the server's name with '_' as row 23 (23 5f: fep.unjis gives '_'
    # too) and a last odd byte (unjis drops it)
    server2 = fj('pimos') + bytes([0x23, 0x5f]) + fj('remote_login_server') + b'\x23'
    s = []
    # 5. the kernel's start from 240 to the shell's prompt, condensed,
    # and its edges that are answered
    s.append((std, [
        sd(18, fepm.FEP_ATTRIBUTES, b''), receive(16000),
        sd(18, fepm.FEP_ATTRIBUTES, b''), receive(20), receive(30), receive(64),  # cut
        sd(17, fepm.CREATE_TIMER, b'', 0, 0), r,
        sd(17, fepm.GET_DATE_TIME), r,                                        # clock 0
        ('ticks', day - 1), sd(17, fepm.GET_DATE_TIME), r,                    # 23:59:59.999
        ('ticks', day), sd(17, fepm.GET_DATE_TIME), r,                        # midnight
        ('ticks', day + 15), sd(17, fepm.GET_DATE_TIME), receive(17), r,      # cut
        ('ticks', (1 << 48) - 1), sd(17, fepm.GET_DATE_TIME), r,              # the top
        ('ticks', 28927 * 16 + 5), sd(17, fepm.GET_DATE_TIME), r,
        sd(17, fepm.CLOSE), r,
        sd(19, fepm.READ_OPEN, b'', 0, 0, fj('pimos:autoload.tbl')), r,       # not held: 5
        sd(19, fepm.READ_OPEN, b'', 0, 0, fj('pimos:pimos.conf')), r,
        sd(19, fepm.GETB, 100), receive(300), sd(19, fepm.FLUSH), r,
        sd(19, fepm.ABORT), r, sd(19, fepm.CLOSE), r,
        sd(27, fepm.READ_OPEN, b'', fj('pmpsi'), b'', fj('me:pimos.init')), r,   # 5
        sd(29, fepm.READ_OPEN, b'', 0, 0, fj('>sys>user>pmpsi>pimos.init')), r,  # 5
        strio(23, fepm.REPLIER), r,
        io(23, 0, b''), r, io(23, 2, 7), r,                       # 0, 2: data not looked at
        io(23, 1, b'\x00\x01' + fj('Login')), r, io(23, 1, b''), r,
        strio(24, fepm.SERVER), r, io(24, 0, fj('local')), r,
        io(24, 1, fj('  ')), r, r,                                # held: nothing comes
        sd(25, fepm.CREATE_STRING_IO, b'', 0, 0, server2), r,
        io(25, 0, fj('tcpip')), r, sd(25, fepm.CLOSE), r,
        strio(26, fepm.USER_DEVICE), r,
        io(26, 0, b'\x00\x05\x00\x00' + fj('pmpsi')), receive(24), receive(30), r,  # cut
        io(26, 0, b'\x00\x05'), r, io(26, 0, b''), r, io(26, 0, b'\x00'), r,
        io(26, 0, b'\x00\x02\x00\x00' + fj('pmpsi')), r,          # n 2: four bytes of it
        io(26, 0, b'\x01'), r,                                    # one byte: n = 1
        sd(26, fepm.ABORT), r, sd(26, fepm.CLOSE), r,
        window(28), r,
        sd(28, 127, 200, 200, 47, 14), r, sd(28, 127, 1, 2, 3, 4, 5, 6), r,  # six arguments
        sd(28, 130, fj('PIMOS')), r, sd(28, 132, 5), r, sd(28, 141), r, sd(28, 142), r,
        sd(28, 143), r, sd(28, 126), r,                           # 126: the listener's window
        sd(28, fepm.PUTB, fj('Shell>> ')), r, sd(28, fepm.FLUSH, 9), r,
        sd(28, fepm.GETL), r,                                     # held
        IDLE, r, r,                                               # the login, to 24
        sd(24, fepm.IO, 1, fj('  ')), r,                          # held again
        IDLE, r,                                                  # getl "dir", to 28
        sd(24, fepm.ABORT), r,                                    # 6
        IDLE, r,                                                  # a login: none held, it waits
        sd(24, fepm.IO, 1, b''), IDLE, r,                         # now answered
        IDLE, r,                                                  # getl "x": none held, waits
        sd(28, fepm.GETL), IDLE, r,
        IDLE, r,                                                  # the script is done
        sd(28, fepm.CLOSE), r]))
    # 6. the devices' sets overlap, and fep.py's order of tests decides:
    # a file that is a timer; a window that is a timer; a hold that
    # outlives its window's close; the lowest device id first
    s.append((std, [
        sd(40, fepm.READ_OPEN, b'', 0, 0, fj('pimos:pimos.logins')), r,
        sd(40, fepm.CREATE_TIMER, b'', 0, 0), r,
        sd(40, fepm.GET_DATE_TIME), r, sd(40, fepm.GETB, 8), r,
        sd(40, fepm.FLUSH), r, sd(40, fepm.CLOSE), r,            # the timer's close first
        sd(40, fepm.GETB, 8), r, sd(40, fepm.CLOSE), r,          # then the file's
        window(41), r, sd(41, fepm.CREATE_TIMER, b'', 0, 0), r,
        sd(41, fepm.CLOSE), r,                                   # the window's close first
        sd(41, fepm.GET_DATE_TIME), r, sd(41, fepm.CLOSE), r,
        window(42), r, sd(42, fepm.GETL, 1, 2), sd(42, fepm.CLOSE), r,   # held, then closed
        sd(42, fepm.ABORT), r,                                   # still held: 6
        strio(-3, fepm.SERVER), r, io(-3, 0, fj('local')), r,
        strio(44, fepm.SERVER), r, io(44, 0, fj('local')), r,
        io(44, 1, b''), io(-3, 1, b''), IDLE, r, r,               # -3 is the lower id
        IDLE, r,                                                  # getl: none held
        sd(-3, fepm.CLOSE), r]))
    # 7. the event under lag, and after a refusal
    s.append((dict(std, lag=1), [
        strio(24, fepm.SERVER), r, r, io(24, 0, fj('local')), r, r, io(24, 1, b''),
        r, IDLE, r, r]))
    s.append((std, [sd(3, fepm.CLOSE), IDLE]))
    # 8. each FepError, one a section
    held_server = [strio(24, fepm.SERVER), io(24, 0, fj('local')), io(24, 1, b'')]
    errs = [
        [sd(18, fepm.FEP_ATTRIBUTES)],                           # no argument
        [sd(18, fepm.FEP_ATTRIBUTES, b'', 0)],                   # two
        [sd(17, fepm.CREATE_TIMER, b'', 0, 0), sd(17, fepm.FEP_ATTRIBUTES, b'')],  # known
        [sd(17, fepm.CREATE_TIMER, b'', 0, 0), sd(17, fepm.CREATE_TIMER, b'', 0, 0)],
        [sd(17, fepm.CREATE_TIMER, b'', 0)],                     # two arguments
        [sd(17, fepm.GET_DATE_TIME)],                            # not a timer
        [sd(17, fepm.CREATE_TIMER, b'', 0, 0), sd(17, fepm.GET_DATE_TIME, 0)],
        [sd(17, fepm.CREATE_TIMER, b'', 0, 0), sd(17, fepm.CLOSE, 0)],
        [strio(23, 'pimos_remote_login_replies')],               # another name
        [strio(23, 'pimos')],
        [sd(23, fepm.CREATE_STRING_IO, b'', 0, 0, 5)],           # an integer name
        [sd(23, fepm.CREATE_STRING_IO, b'', 0, fj(fepm.REPLIER))],    # three arguments
        [strio(23, fepm.REPLIER), strio(23, fepm.SERVER)],       # known
        [io(23, 0, b'')],                                        # not string-I/O
        [strio(23, fepm.REPLIER), sd(23, fepm.IO, 0)],           # one argument
        [strio(23, fepm.REPLIER), io(23, b'', b'')],             # a string command
        [strio(23, fepm.REPLIER), io(23, 3, b'')],
        [strio(23, fepm.REPLIER), io(23, 1, 9)],                 # an integer text
        [strio(24, fepm.SERVER), io(24, 0, fj('remote'))],
        [strio(24, fepm.SERVER), io(24, 0, 1)],
        [strio(24, fepm.SERVER), io(24, 1, b'')],                # not listening
        [strio(24, fepm.SERVER), io(24, 2, b'')],
        held_server + [io(24, 0, fj('local'))],                  # held
        [strio(26, fepm.USER_DEVICE), io(26, 0, 7)],
        [strio(26, fepm.USER_DEVICE), io(26, 1, b'')],
        [window(28), window(28)],
        [window(28), sd(28, fepm.PUTB)],                         # putb, no text
        [window(28), sd(28, fepm.PUTB, 5)],                      # an integer text
        [window(28), sd(28, 131)],                               # a call fep.py does not answer
        [window(28), sd(28, fepm.GETL), sd(28, fepm.GETL)],      # held
        [window(28), sd(28, fepm.GETL), sd(28, fepm.PUTB, b'')],
        [window(28), sd(28, fepm.CLOSE, 0)],
        [window(28), sd(28, fepm.GETL), sd(28, fepm.ABORT, 0)],
        [sd(28, fepm.PUTB, b'')],                                # not a window
        [sd(16, fepm.APPEND_OPEN, b'', 0, 0, b''), sd(16, fepm.FLUSH)],   # flush, appending
        [sd(40, fepm.READ_OPEN, b'', 0, 0, fj('pimos:pimos.conf')), sd(40, fepm.FLUSH, 1)],
        [sd(40, fepm.READ_OPEN, b'', 0, 0, fj('pimos:pimos.conf')), window(40)],  # known
        [sd(40, fepm.READ_OPEN, b'', 0, 0, fj('pimos:pimos.conf')), strio(40, fepm.SERVER)],
        [sd(40, fepm.READ_OPEN, b'', 0, 0, fj('pimos:pimos.conf')), sd(40, fepm.FEP_ATTRIBUTES, b'')],
    ]
    for e in errs:
        s.append((std, e))
    # 9. the user device's n with its high byte set (256: the slice runs
    # to the data's end); added when an injection went unnoticed
    s.append((std, [strio(26, fepm.USER_DEVICE), r,
                    io(26, 0, b'\x01\x00\x00\x00' + fj('pmpsi')), r]))
    # 10. what fep.py answers since 2026-11-24 for a typed shutdown
    # (docs/binary_reverse_engineering.md 1.4 "A command typed"): the
    # string-I/O window pimos_standard_io_window, its 104 130 141 111
    # [1, ""] (data not looked at, but putb's), its getl held and
    # answered by the event as a window's, its close; then {-1, 80}
    # (terminate): no reply, and the device goes on
    s.append((std, [
        strio(24, fepm.SERVER), r, io(24, 0, fj('local')), r, io(24, 1, b''), r,
        strio(31, fepm.STD_WINDOW), r,
        io(31, 104, b'\x00\x01'), r, io(31, 104, 324), r,
        io(31, 130, fj('SHUTDOWN')), r, io(31, 141, b''), r, io(31, 141, 0), r,
        io(31, 111, fj('Really(yes/no)?')), r, io(31, 111, b''), receive(12), r,  # cut
        io(31, 110, b''), r,                                      # held
        IDLE, r,                                                  # the login, to 24
        IDLE, r,                                                  # getl "dir", to 31
        io(31, 110, 0), r, IDLE, r,                               # a login: none held
        IDLE, r,                                                  # nothing held
        sd(31, fepm.CLOSE), r,
        sd(-1, fepm.TERMINATE), r, r,                             # nothing comes
        tur_at(7), sd(-1, fepm.TERMINATE), r,                     # again: noted again
        sd(24, fepm.ABORT), r]))
    errs = [
        [strio(31, fepm.STD_WINDOW), io(31, 111, 5)],            # an integer text
        [strio(31, fepm.STD_WINDOW), io(31, 112, b'')],          # not answered
        [strio(31, fepm.STD_WINDOW), io(31, 127, b'')],
        [strio(31, fepm.STD_WINDOW), io(31, b'', b'')],          # a string command
        [strio(31, fepm.STD_WINDOW), io(31, 110, b''), io(31, 104, b'')],   # held
        [strio(31, fepm.STD_WINDOW), sd(31, fepm.PUTB, fj('x'))],  # a window's putb: not one
        [strio(31, 'pimos_standard_io_windows')],                # another name
        [sd(5, fepm.TERMINATE)],                                 # not device -1
        [sd(-1, fepm.TERMINATE, 0)],                             # an argument
    ]
    for e in errs:
        s.append((std, e))
    return s


# ---- the kernel part: PIMOS's start ----------------------------------
# the first ten answered commands (docs/binary_reverse_engineering.md 1.4)
KERNEL_FIRST = [(7, 0x00), (7, 0x12)] + [(u, 0x00) for u in (5, 4, 3, 2, 1, 0)] + \
    [(7, fepm.SEND), (7, fepm.RECEIVE)]


def record_kernel(pkl, lines=()):
    import pickle
    import longrun_ipl as lr
    with open(pkl, 'rb') as f:
        m, loaded, info = pickle.load(f)
    Recording.calls = []
    fepm.Fep = Recording
    try:
        lr.go(m, loaded, info, [], True, lines)
    finally:
        fepm.Fep = ORIGINAL
    dev = Recording.made
    opts = dict(getb_unit=dev.getb_unit, getb_bytes=dev.getb_bytes or 0, lag=int(dev.lag),
                max_buffer=dev.MAX_BUFFER)
    items, seen = tape_of(Recording.calls)
    script = ORIGINAL(None, lines=lines).script if lines else None
    if replay([(opts, items)], [OBJECTS], script) != seen:
        raise SystemExit('record_fep: kernel: a replay into a fresh fep.Fep differs')
    calls = [c for c in items if c[0] != 'ticks']
    done = [c for c, a in zip(calls, seen) if a[0] == 'D']
    if [(c[0], c[2][0]) for c in done[:10]] != KERNEL_FIRST:
        raise SystemExit('record_fep: kernel: the first answered commands are %r'
                         % [(c[0], c[2][:1].hex()) for c in done[:10]])
    g = info['go']
    ncmd = sum(1 for c in calls if is_command(c))
    print('%-12s %3d calls (%d answered, %d not ready), %d idle (%d answered); go: %d '
          'instructions, stop: %s; held at the end %r'
          % ('kernel', ncmd, len(done), ncmd - len(done), calls.count(IDLE),
             seen.count(('I', True)), g['instructions'], g['stop'], g['fep'].get('held')))
    print('    console %r' % (g['console'],))
    print('    log %r; terminated %r' % (dev.log, dev.terminated))
    sizes(opts, items, [OBJECTS])
    return [(opts, items)]


def sizes(opts, items, files):
    """What the emulator's limits of OURS must hold for a tape: the
    largest request message, the most replies queued and devices of
    each kind at once, the most arguments of each command."""
    f = ORIGINAL(open_file_for(files), **device_kwargs(opts))
    most = dict(queued=0, files=0, appending=0, timers=0, strio=0, windows=0, held=0,
                listening=0)
    args = {}
    for c in items:
        if c[0] == 'ticks':
            f.ticks = c[1]
            continue
        n = len(f.messages)
        if c == IDLE:
            f.idle()
        else:
            f.command(*c)
        for d, _i, msg in f.messages[n:]:
            if d == '>':
                args[msg[0]] = max(args.get(msg[0], 0), len(msg) - 1)
        most['queued'] = max(most['queued'], len(f.replies))
        for k in most:
            if k != 'queued':
                most[k] = max(most[k], len(getattr(f, k)))
    print('    largest request message %d bytes; most at once %r; arguments by command %r'
          % (largest_request([c for c in items if is_command(c)]), most, sorted(args.items())))


# ---- tapes -----------------------------------------------------------
def script_words(script):
    """A script as a tape's `script` line has it: `login` (fep.LOGIN),
    `getl=TEXT` (a line, no spaces)."""
    out = []
    for kind, what in script:
        if kind == 'login' and what == fepm.LOGIN:
            out.append('login')
        elif kind == 'getl' and ' ' not in what:
            out.append('getl=' + what)
        else:
            raise ValueError('a script event a tape cannot hold: %r' % ((kind, what),))
    return out


# why a tape last changed, as its header says (OURS)
NOTES = {
    'late': 'Re-recorded 2026-11-24 after the merger change (the merger acts at '
            'unification, docs/pimm_semantics.md merge): RECEIVE retries move; and '
            'the clock (ticks) lines added',
    'one file': 'Re-recorded 2026-11-24: the clock (ticks) lines added; the commands as before',
    'two files': 'Re-recorded 2026-11-24: the clock (ticks) lines added; the commands as before',
    'characters': 'Re-recorded 2026-11-24: the clock (ticks) lines added; the commands as before',
    'odd': 'Re-recorded 2026-11-24: the clock (ticks) lines added; the commands as before',
    'small buffer': 'Re-recorded 2026-11-24: the clock (ticks) lines added; the commands as before',
    'direct kernel': '2026-11-24: fep.py answers 60 on the append-opened file, the '
                     'string-I/O window pimos_standard_io_window and {-1, 80}; their '
                     'sections added, the close on an appending device out of the errors',
    'kernel': 'Re-recorded 2026-11-24 after the merger change (the merger acts at '
              'unification, docs/pimm_semantics.md merge: the conversation moves), and '
              'to PIMOS END: --kernel PKL --type shutdown --type yes; and again with '
              'the login ID 0 (fep.py LOGIN, P-f3): the replier texts\' element 0 moves',
}


def write_tape(path, label, files, sections, script=None):
    lines = ['# %s: recorded by ref/pimm/record_fep.py (OURS); the commands only' % label]
    if label in NOTES:
        lines.append('# ' + NOTES[label])
    lines += ['part %s' % SLUG[label],
             'files %s' % ' '.join(files)]
    if script is not None:
        lines.append('script %s' % ' '.join(script_words(script)))
    for opts, cmds in sections:
        lines.append('config getb_unit=%(getb_unit)d getb_bytes=%(getb_bytes)d lag=%(lag)d '
                     'max_buffer=%(max_buffer)d' % opts)
        for item in cmds:
            if item[0] == 'ticks':
                lines.append('ticks %d' % item[1])
                continue
            if item == IDLE:
                lines.append('idle')
                continue
            unit, lun, c, length, direction, data = item
            lines.append('cmd %d %d %d %d %s %s' % (unit, lun, direction, length, c.hex(),
                                                    data.hex() or '-'))
    text = '\n'.join(lines) + '\n'
    if path is not None:
        with open(path, 'w') as fh:
            fh.write(text)
    return text


def read_tape(path):
    """-> (part, files, [(options, [command, ...]), ...], script), the
    script None for fep.py's own"""
    part, files, sections, script = None, [], [], None
    for line in open(path):
        w = line.split()
        if not w or w[0].startswith('#'):
            continue
        if w[0] == 'part':
            part = w[1]
        elif w[0] == 'files':
            files = w[1:]
        elif w[0] == 'script':
            script = [('login', fepm.LOGIN) if x == 'login' else ('getl', x[len('getl='):])
                      for x in w[1:]]
        elif w[0] == 'config':
            sections.append(({k: int(v) for k, v in (x.split('=') for x in w[1:])}, []))
        elif w[0] == 'cmd':
            unit, lun, direction, length = map(int, w[1:5])
            data = b'' if w[6] == '-' else bytes.fromhex(w[6])
            sections[-1][1].append((unit, lun, bytes.fromhex(w[5]), length, direction, data))
        elif w[0] == 'ticks':
            sections[-1][1].append(('ticks', int(w[1])))
        elif w[0] == 'idle':
            sections[-1][1].append(IDLE)
        else:
            raise ValueError('%s: %r' % (path, line))
    return part, files, sections, script


def record(label, files, device):
    Recording.calls = []
    fepm.Fep = Recording
    try:
        m, v, opened = rs.boot(rs.listing(files), **device)
    finally:
        fepm.Fep = ORIGINAL
    bad = rs.check(label, files, device, m, v, opened)
    if bad:
        raise SystemExit('record_fep: part %s fails ref_scsi.check: %r' % (label, bad[:3]))
    opts = options(device)
    cmds, seen = tape_of(Recording.calls)
    if replay([(opts, cmds)], files) != seen:
        raise SystemExit('record_fep: part %s: a replay into a fresh fep.Fep differs' % label)
    done = sum(1 for a in seen if a[0] == 'D')
    if done != rs.PINNED[label][0]:
        raise SystemExit('record_fep: part %s: %d commands, PINNED %d' % (label, done,
                                                                           rs.PINNED[label][0]))
    f = m.fep
    print('%-12s %3d calls (%d answered, %d not ready); most open at once %d; largest '
          'request message %d bytes; most replies queued %d'
          % (label, len(cmds), done, len(cmds) - done, most_open(f), largest_request(cmds),
             most_queued(opts, cmds, files)))
    return [(opts, cmds)]


def most_open(f):
    most, opened = 0, set()
    for d, i, msg in f.messages:
        if d == '>' and msg[0] == fepm.READ_OPEN:
            opened.add(i)
            most = max(most, len(opened))
        if d == '>' and msg[0] == fepm.CLOSE:
            opened.discard(i)
    return most


def largest_request(cmds):
    return max([len(c[5]) - 8 for c in cmds if is_command(c) and c[4] == 1] or [0])


def most_queued(opts, cmds, files):
    f = ORIGINAL(open_file_for(files), **device_kwargs(opts))
    most = 0
    for c in cmds:
        if is_command(c):
            f.command(*c)
        most = max(most, len(f.replies))
    return most


def main(argv):
    parts = list(rs.PARTS) + [('direct', [rs.HASH], {}), ('direct kernel', [OBJECTS], {})]
    if '--kernel' in argv:
        parts = [('kernel', [OBJECTS], {})]
    elif '--part' in argv:
        want = argv[argv.index('--part') + 1]
        parts = [p for p in parts if p[0] == want or SLUG[p[0]] == want]
    os.makedirs(TAPES, exist_ok=True)
    bad = 0
    for label, files, device in parts:
        script = None
        if label == 'direct':
            sections = direct_sections()
        elif label == 'direct kernel':
            sections = direct_kernel_sections()
            script = DIRECT_KERNEL_SCRIPT
        elif label == 'kernel':
            # --type LINE ...: the lines typed (longrun_ipl.py's --type),
            # the tape's script then fep.py's for them
            lines = [argv[i + 1] for i, a in enumerate(argv) if a == '--type']
            sections = record_kernel(argv[argv.index('--kernel') + 1], lines)
            if lines:
                script = ORIGINAL(None, lines=lines).script
        else:
            sections = record(label, files, device)
        path = os.path.join(TAPES, SLUG[label] + '.tape')
        if '--check' in argv:
            if write_tape(None, label, files, sections, script) != open(path).read():
                print('record_fep: %s differs from a recording now' % path)
                bad += 1
        else:
            write_tape(path, label, files, sections, script)
            print('  wrote %s' % os.path.relpath(path))
    if bad:
        print('record_fep: FAIL')
        return 1
    print('record_fep: %s' % ('PASS (the tapes are what a recording gives)' if '--check' in argv
                              else 'done'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
