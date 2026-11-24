#!/usr/bin/env python3
"""Record the SCSI commands the IPL gives the FEP, as tapes for the
Bluespec FEP emulator's bench (bsv/PimmFepEmuTb.bsv, bsv/run_fepemu.sh).

    python3 ref/pimm/record_fep.py            record every part (slow: it
                                              runs ref_scsi.py's parts, ~3 min)
    python3 ref/pimm/record_fep.py --part odd one part
    python3 ref/pimm/record_fep.py --check    the tapes on disk are what a
                                              recording gives now

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
        'late': 'late', 'odd': 'odd', 'small buffer': 'small_buffer', 'direct': 'direct'}


class Recording(ORIGINAL):
    """fep.Fep, noting each call and its answer."""
    calls = None

    def command(self, unit, lun, cdb, length, direction, data):
        got = ORIGINAL.command(self, unit, lun, cdb, length, direction, data)
        Recording.calls.append(((unit, lun, bytes(cdb), length, direction,
                                 bytes(data) if direction == 1 else b''), got))
        return got


def options(device):
    return dict(getb_unit=device.get('getb_unit', 1), getb_bytes=device.get('getb_bytes') or 0,
                lag=int(bool(device.get('lag'))),
                max_buffer=device.get('max_buffer') or ORIGINAL.MAX_BUFFER)


def device_kwargs(opts):
    return dict(getb_unit=opts['getb_unit'], getb_bytes=opts['getb_bytes'] or None,
                lag=bool(opts['lag']), max_buffer=opts['max_buffer'])


def open_file_for(files):
    """ref_scsi.boot's open_file, outside a machine: the list of OURS
    and the held .sav files, by the path's bytes."""
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


def replay(sections, files):
    """Each section's commands into a fresh fep.Fep: the answers, an
    answer being ('D', result, bytes), ('N',) or ('E', message); after
    an E the rest of the section is E too (fep.py's caller has raised)."""
    out = []
    for opts, cmds in sections:
        f = ORIGINAL(open_file_for(files), **device_kwargs(opts))
        dead = None
        for unit, lun, cdb, length, direction, data in cmds:
            if dead is not None:
                out.append(('E', 'after: ' + dead))
                continue
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


# ---- tapes -----------------------------------------------------------
def write_tape(path, label, files, sections):
    lines = ['# %s: recorded by ref/pimm/record_fep.py (OURS); the commands only' % label,
             'part %s' % SLUG[label],
             'files %s' % ' '.join(files)]
    for opts, cmds in sections:
        lines.append('config getb_unit=%(getb_unit)d getb_bytes=%(getb_bytes)d lag=%(lag)d '
                     'max_buffer=%(max_buffer)d' % opts)
        for unit, lun, c, length, direction, data in cmds:
            lines.append('cmd %d %d %d %d %s %s' % (unit, lun, direction, length, c.hex(),
                                                    data.hex() or '-'))
    text = '\n'.join(lines) + '\n'
    if path is not None:
        with open(path, 'w') as fh:
            fh.write(text)
    return text


def read_tape(path):
    """-> (part, files, [(options, [command, ...]), ...])"""
    part, files, sections = None, [], []
    for line in open(path):
        w = line.split()
        if not w or w[0].startswith('#'):
            continue
        if w[0] == 'part':
            part = w[1]
        elif w[0] == 'files':
            files = w[1:]
        elif w[0] == 'config':
            sections.append(({k: int(v) for k, v in (x.split('=') for x in w[1:])}, []))
        elif w[0] == 'cmd':
            unit, lun, direction, length = map(int, w[1:5])
            data = b'' if w[6] == '-' else bytes.fromhex(w[6])
            sections[-1][1].append((unit, lun, bytes.fromhex(w[5]), length, direction, data))
        else:
            raise ValueError('%s: %r' % (path, line))
    return part, files, sections


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
    cmds = [c for c, _ in Recording.calls]
    seen = [('N',) if g is None else ('D', g[0], bytes(g[1])) for _, g in Recording.calls]
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
    return max([len(c[5]) - 8 for c in cmds if c[4] == 1] or [0])


def most_queued(opts, cmds, files):
    f = ORIGINAL(open_file_for(files), **device_kwargs(opts))
    most = 0
    for c in cmds:
        f.command(*c)
        most = max(most, len(f.replies))
    return most


def main(argv):
    parts = list(rs.PARTS) + [('direct', [rs.HASH], {})]
    if '--part' in argv:
        want = argv[argv.index('--part') + 1]
        parts = [p for p in parts if p[0] == want or SLUG[p[0]] == want]
    os.makedirs(TAPES, exist_ok=True)
    bad = 0
    for label, files, device in parts:
        sections = direct_sections() if label == 'direct' else record(label, files, device)
        path = os.path.join(TAPES, SLUG[label] + '.tape')
        if '--check' in argv:
            if write_tape(None, label, files, sections) != open(path).read():
                print('record_fep: %s differs from a recording now' % path)
                bad += 1
        else:
            write_tape(path, label, files, sections)
            print('  wrote %s' % os.path.relpath(path))
    if bad:
        print('record_fep: FAIL')
        return 1
    print('record_fep: %s' % ('PASS (the tapes are what a recording gives)' if '--check' in argv
                              else 'done'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
