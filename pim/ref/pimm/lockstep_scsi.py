#!/usr/bin/env python3
"""Lockstep: scsi_init and scsi_command, the device on a tape.

    python3 ref/pimm/lockstep_scsi.py --script FILE     write the script and its tape
    sim_pimm_driver | python3 ref/pimm/lockstep_scsi.py compare
    python3 ref/pimm/lockstep_scsi.py --part N ...      the same for IPL part N (1..6)
    python3 ref/pimm/lockstep_scsi.py --reference       the reference alone, and
                                                        ref_scsi.py's IPL parts

The two SCSI built-ins (22:DF, 22:DB), whose firmware is lost: their
behaviour is OURS, the reference model's (pimm.py i_scsi_init,
i_scsi_command, scsi_poll; on the core bsv/PimmScsiBox.bsv).  The
device is ref/pimm/fep.py on the reference model; the bench answers
from the tape the reference recorded (driver.py "The device tape").
Every command is a B line on both models, printed by the bench from
what the CORE put on its port: so the CDBs, directions, lengths and a
SEND's bytes are compared line by line, and only the answers replayed.

Parts, one machine, at the real sites (scsi:create/2, which runs
scsi_init, and scsi:command_executer/2, which runs scsi_command on each
command(V, Data, TransferredLength, Id, Result) of its stream; asm/
kl1decomp.py scsi).  The device: unit 7, a buffer size of 1000 (not the
16000 of scsi_blt.kl1, so that the size is seen to come from it), every
command's buffer 61 bytes (an odd length: a pad of three) filled with
A0h, A1h, ... beyond what is put in it:
  create        scsi:create(0, B): B = normal(_); scsi_init asks the
                device (B init)
  test unit ready  TEST UNIT READY: Data the buffer itself, length 0,
                Id 0, Result 0
  receive, nothing yet  a RECEIVE before anything is sent: the device
                has no reply, so Id and NewObj at once and Data,
                TransferredLength, Result unbound; a goal waits on that
                Result (b_add at its stub: Result + 5); the machine
                runs dry and the device is polled (POLL): still nothing
  send          a SEND of read_open (201, a 44-byte packet): it
                finishes, and the device has moved, so the waiting
                RECEIVE is given to it again inside the same
                instruction: its 16-byte reply is copied into a new
                string (the reply, then the buffer's bytes 16..60), its
                three variables are bound and the waiting goal is woken
                (Result + 5 = 5)
  receive       a SEND of getb (210, 20 bytes) and two RECEIVEs: one of
                22 bytes (the 40-byte reply is cut by the device, flag
                1: TransferredLength = Length) and one of 61 (the rest,
                26 bytes): byte counts that are not a multiple of four
                (the copy's word with received and old bytes, the
                tape's last word half padding)
  late          a SEND of close (60) and a RECEIVE the device refuses
                once (this test's device, not fep.py's): it waits, the
                machine runs dry, POLL gives it again and it finishes
                there, waking its waiting goal
  element       TEST UNIT READY with its Length not yet bound: the
                built-in waits on the vector's element (its stub's goal,
                as string_operation's), and runs when it is bound
Checked on the reference: every output against values worked out here
(the reply bytes from fep.pack_message, the rest of the buffer by hand),
the B lines against the commands this test meant to send, written out
here, the device's finished commands in order, two commands that
waited, the trace pinned.

With --part N, ref_scsi.py's IPL part N (1 one file, 2 two files, 3
characters, 4 late, 5 odd, 6 small buffer), each its own script on a
fresh machine and device (bsv/run_pimm_lockstep.sh's scsi@N): the body
of ipl:boot0/0 as ref_scsi.boot makes it, through driver.Script, the
IPL reading its list and files through its own SCSI stack; RUN, then
POLL and RUN while a poll finishes a command (built with Script.live),
then a last POLL.  Checked: ref_scsi.check (the files opened, Files,
Loaded, the console, the first commands against
docs/binary_reverse_engineering.md 1.3, the requests per device, the
heap cells), the B lines against the device's own record, the trace
pinned (PINNED_IPL).  They need the merger's vector input
(scsi_fep_general:request_device_io/5), on both models since master's
d1beeb7b.

On the reference, 2026-11-23: the script leaves 3 goals waiting
(scsi:create/2's merger input, command_executer/2 and
request_manager/3 on their streams, as read from the code; not
checked); the six IPL parts as scripts pass ref_scsi.check and
the bus check; after the merge of d1beeb7b (24 to 28 lines more each
than before it, where the reference took the merger's vectors under
Machine.ahead; the cause is not traced line by line) 1,458,322 /
2,683,031 / 2,654,349 / 2,683,403 / 324,652 / 71,735 trace lines
(late: 47 B lines, 7 polls that finish), the pins until 2026-11-24.
Re-pinned for the merger timing change (2026-11-24, docs/
pimm_semantics.md merge: a woken goal of merge_in goes on the
merger's list, taken before the ready queue): 1,458,515 / 2,687,853 /
2,659,308 / 2,688,840 / 324,527 / 71,510, both models identical; the
first part's 7 (scsi) unchanged at 1,553.  The wire and the FEP's
messages of every IPL part are the same before and after (ref_scsi.py,
compared by hash).

Observed fault injections into bsv/PimmScsiBox.bsv (the last but three
into the exec stage's hook in PimmStages.bsv), 2026-11-23, each from a
backup copy, `bsv/run_pimm_lockstep.sh scsi` only, restored and
compared byte for byte; the first difference:
  a SEND's first byte flipped          send, line 98: the B line's bytes
  TransferredLength one too many       send, line 118: the waiting
                                       RECEIVE's TL bound to 17 for 16
  RECEIVE written one cell off         send, line 101: M 32978 for 32977
  Id not counted (a finished command)  receive, nothing yet, line 109:
                                       R 4 = 0 for 1
  the waiting path binding all at once receive, nothing yet, line 107:
                                       Data the buffer, not a variable
  Result nonzero                       test unit ready, line 105: R 9
  NewObj the vector, not Obj           test unit ready, line 106: R 1
  no poll inside a finished command    send, line 99: no B line for the
                                       waiting RECEIVE
  the rest of the buffer zero          send, line 105: M 32981
  the buffer size 16000, not the       create, line 31: M 32780
  device's
  Id not counted (a command that waits) send, line 125: the SEND's Id
                                       1 for 2
NOT caught (observed): the copy's pad bytes taken from the old
buffer's memory rather than zero: the lockstep PASSes, every buffer
here having been made with zero pad.
Not injected (by reading, not caught either): the CDB and buffer read
again at a poll where the reference keeps their bytes (nothing changes
them between); the waiting list's order with two or more waiting (one
at a time is the most run, here and in ref_scsi.py's "late").

Observed fault injections against all seven runs (the unit script and
--part 1..6), 2026-11-24: eleven, each in its own copy of pim/ (bsv/
PimmScsiBox.bsv, the eighth into PimmStages.bsv's scsiInit1), the file
backed up, injected, rebuilt (compile.log showing the package
recompiled), the seven run one by one, restored with cp and compared
byte for byte with the backup and with the committed file.  The
first difference, unit script / IPL parts:
  the CDB's words byte-reversed       all 7.  scsi: receive, nothing
                                      yet, line 103 (the TEST UNIT
                                      READY's CDB is all zero: the same
                                      reversed); @1..5 line 29,759, @6
                                      line 10,399: the first SEND's B line
  unit and LUN swapped                all 7.  scsi: test unit ready,
                                      line 101; @1..6 line 1,250: B 0 7
  the last byte received dropped      all 7.  scsi: send, line 104;
                                      @1/@5 line 75,395, @2/@3 79,597,
                                      @4 99,794, @6 25,059: an M line
  TransferredLength the length asked  all 7.  scsi: send, line 118;
  for, for a RECEIVE too              @1..3/@5 line 34,421 (R 2 = 16000
                                      for 16; @6 512), @4 line 54,458
  Result the device's with bit 0      all 7.  scsi: test unit ready,
  flipped                             line 105; @1..6 line 1,254: R 9
  Info's buffer size one less         all 7.  scsi: create, line 31;
                                      @1..6 line 396 (3e7f for 3e80;
                                      @6 1ff for 200)
  Info's 8 and 4 swapped              all 7.  scsi: create, line 32;
                                      @1..6 line 397
  TargetInterruptVector and Info to   all 7.  scsi: create, line 30;
  each other's register (the hook)    @1..6 line 395: R 2 for R 1
  a command not ready at a poll       scsi only: send, line 99 (no B
  dropped from the waiting list       line for the RECEIVE given again)
  a poll taking "not ready" as ready  scsi only: receive, nothing yet,
  with nothing received               line 171 (its variables bound)
  the copy's pad bytes from the old   NONE of the 7
  buffer's memory, not zero
Not caught by the IPL parts, and why (counted on the reference from
ipl_build(n)'s tape and fep.wire): no command of any part is not ready
at a poll ("late" has 15 not-ready answers, all to the command itself,
each finished at its first retry; the other parts none), so the two
poll injections are caught only by the unit script's "receive, nothing
yet", whose first POLL finds nothing.  The pad: the IPL's buffers are
16000 and 512 bytes (no pad), the unit script's 61 (pad 3) made with
zero pad, and every string the machine makes has zero pad, so the
mutation is not observable on any input the core can be given (not a
hole a part could close).  Every Result on every tape is 0 and every
byte count a multiple of four in the IPL parts (hence a flip, not a
forced 0, for Result).  By reading, not injected: the poll's count
(scsiPolled) is discarded by the bench (PimmDriverTb.bsv rule polled),
so no part can catch a wrong count; the script's flow, not the count,
decides the next RUN.

Not run: a vector not of seven, a seventh element not 0, a length over
the buffer, a CDB or buffer not of 8-bit elements, the device giving
more bytes than asked (refusals, which the driver cannot play);
scsi_init without a device; a fifth waiting command.
"""
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import fep as fepm  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=7, lines=1553)
# the IPL parts (--part 1..6): trace lines, one part each
PINNED_IPL = {'one file': 1458515, 'two files': 2687853, 'characters': 2659308,
              'late': 2688840, 'odd': 324527, 'small buffer': 71510}
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
NIL = (pimm.ATOM, 0)
BUFFER = 61
SIZE = 1000
PATH = bytes.fromhex('23702369')             # 'pi' in two-byte JIS: the file's name
FILE = b'PIM/m on a SCSI tape.'               # 21 bytes, the getb asks for 20
PAD = bytes((0xa0 + i) & 0xff for i in range(BUFFER))


def packet(dev, args, flag=0):
    return struct.pack('>ii', dev, flag) + fepm.pack_message(args)


class Device(fepm.Fep):
    """fep.py's device, refusing the device calls numbered in `refuse`
    once each (this test's, for the late part)."""

    def __init__(self, refuse):
        fepm.Fep.__init__(self, lambda p: FILE if p == PATH else None, max_buffer=SIZE)
        self.refuse, self.calls = refuse, 0

    def command(self, *a):
        k = self.calls
        self.calls += 1
        if k in self.refuse:
            return None
        return fepm.Fep.command(self, *a)


def cdb(op, lun, n):
    return bytes([op, lun << 5, n >> 16 & 255, n >> 8 & 255, n & 255])


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    P = lambda mod, pred: pimm.predicate(im, mod, pred)   # noqa: E731
    stubs = pimm.Machine().stubs
    refuse = []
    s = driver.Script()

    def make():
        m = pimm.Machine()
        m.fep = Device(refuse)
        return m
    s.make = make
    want = []        # (part, [expected terms of its OUTs])
    bus = []         # the B lines this test means the core to put on the bus

    def calls():
        return s.live().fep.calls

    def command(unit, lun, c, length, direction, data=b'', unbound=None):
        """command_executer([command(V, Data, TL, Id, Result)], 1), V =
        {Unit, LUN, CDB, Length, Dir, Buffer, 0}: the long vector
        {VDESC}{7}{7} and its seven elements, consecutive cells.  Data,
        TL, Id, Result in slots 10..13; an element left unbound in slot
        2."""
        buf = data + PAD[len(data):]
        s.string(3, 8, list(c))
        s.string(4, 8, list(buf))
        s.newvar(5)                                    # the descriptor
        for _ in range(2):                             # the length, twice
            s.newvar(6)
            s.unifyc(6, I(7))
        elems = [I(unit), I(lun), ('slot', 3), I(length), I(direction), ('slot', 4), I(0)]
        for i, e in enumerate(elems):
            sl = 7 if i == 0 else 2 if i == unbound else 6
            s.newvar(sl)
            if i == unbound:
                continue
            if e[0] == 'slot':
                s.unify(sl, e[1])
            else:
                s.unifyc(sl, e)
        s._op(driver.PTR, 6, 7, (pimm.VDESC, 0))
        s.unify(5, 6)
        s._op(driver.PTR, 15, 5, (pimm.VECT0 + 15, 0))
        s.vector(14, 8, [A('command'), ('slot', 15), None, None, None, None])
        s.cons(5, 6, ('slot', 14), NIL)
        s.arg(1, 5)
        s.argc(2, I(1))
        s.spawn(P('scsi', 'command_executer/2'), 2)
        s.run()
        return buf

    def line(unit, lun, c, direction, length, buf):
        out = buf[:length] if direction == 1 else b''
        bus.append('B %d %d %s %d %d%s' % (unit, lun, c.hex(), direction, length,
                                           ' ' + out.hex() if out else ''))

    def outs(*slots):
        for k in slots:
            s.out(k)

    def keep(a, b):
        s._op(driver.PTR, a, b, (pimm.REF, 0))         # slot a := the variable in slot b

    def waiter():
        """b_add(Result, 5, X) at its stub, Result in slot 0, X in 1."""
        s.newvar(1)
        s.arg(1, 0)
        s.argc(2, I(5))
        s.arg(3, 1)
        s.spawn(stubs['b_add']['addr'], 3)

    TUR = cdb(fepm.TEST_UNIT_READY, 0, 0)

    def send(args, ident):
        p = packet(0, args)
        c = cdb(fepm.SEND, 0, len(p))
        buf = command(7, 0, c, len(p), 1, p)
        line(7, 0, c, 1, len(p), buf)
        outs(10, 11, 12, 13)
        return [(8, list(buf)), len(p), ident, 0]

    def receive(n):
        c = cdb(fepm.RECEIVE, 1, n)
        buf = command(7, 1, c, n, 2)
        line(7, 1, c, 2, n, buf)
        return c, buf

    def got(reply, buf):
        return (8, list(reply + buf[len(reply):]))

    # 1. scsi_init at its site
    s.label('create')
    s.newvar(0)
    s.argc(1, I(0))
    s.arg(2, 0)
    s.spawn(P('scsi', 'create/2'), 2)
    s.run()
    s.out(0)
    bus.append('B init')
    want.append(('create', [('normal', None)]))

    # 2. TEST UNIT READY
    s.label('test unit ready')
    buf = command(7, 0, TUR, 0, 0)
    line(7, 0, TUR, 0, 0, buf)
    outs(10, 11, 12, 13)
    want.append(('test unit ready', [(8, list(buf)), 0, 0, 0]))

    # 3. a RECEIVE with nothing to receive: it waits
    s.label('receive, nothing yet')
    c3, buf3 = receive(BUFFER)
    outs(10, 11, 12, 13)
    keep(0, 13)                     # its Result
    keep(2, 10)                     # its Data
    waiter()
    s.run()
    s.poll()                        # the machine is dry: the device still has nothing
    line(7, 1, c3, 2, BUFFER, buf3)
    s.run()
    s.out(1)
    want.append(('receive, nothing yet', [None, None, 1, None, None]))

    # 4. a SEND: and the waiting RECEIVE finishes in the same instruction
    s.label('send')
    exp = send([fepm.READ_OPEN, b'', 0, 0, PATH], 2)
    line(7, 1, c3, 2, BUFFER, buf3)                  # given again: the device has moved
    s.run()
    outs(0, 1, 2)
    exp += [0, 5, got(packet(0, [fepm.NORMAL]), buf3)]
    want.append(('send', exp))

    # 5. getb, the reply in two pieces
    s.label('receive')
    exp = send([fepm.GETB, 20], 3)
    reply = packet(0, [fepm.NORMAL, FILE[:20]])
    first = reply[:4] + struct.pack('>i', 1) + reply[8:22]
    rest = reply[:8] + reply[22:]
    for ident, n, piece in ((4, 22, first), (5, BUFFER, rest)):
        c, buf = receive(n)
        outs(10, 11, 12, 13)
        exp += [got(piece, buf), len(piece), ident, 0]
    want.append(('receive', exp))

    # 6. close, its reply refused once: the poll at the machine's dry end
    s.label('late')
    exp = send([fepm.CLOSE], 6)
    refuse.append(calls())
    c, buf = receive(BUFFER)
    outs(12)
    keep(0, 13)
    keep(2, 10)
    waiter()
    s.run()
    s.poll()
    line(7, 1, c, 2, BUFFER, buf)
    s.run()
    outs(0, 1, 2)
    exp += [7, 0, 5, got(packet(0, [fepm.NORMAL]), buf)]
    want.append(('late', exp))

    # 7. an element not yet bound
    s.label('element')
    buf = command(7, 0, TUR, 0, 0, unbound=3)
    outs(12)
    s.unifyc(2, I(0))
    s.run()
    line(7, 0, TUR, 0, 0, buf)
    outs(10, 11, 12, 13)
    want.append(('element', [None, (8, list(buf)), 0, 8, 0]))
    return s, want, bus


WIRE = ['TEST UNIT READY', 'SEND', 'RECEIVE', 'SEND', 'RECEIVE', 'RECEIVE', 'SEND', 'RECEIVE',
        'TEST UNIT READY']


def check(s, m, want, bus, parts):
    bad = []
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(None if m.unbound(w) else m.term(w))
    for name, exp in want:
        if got.get(name) != exp:
            bad.append((name, got.get(name), exp))
    lines = [ln for p in parts.values() for ln in p if ln.startswith('B ')]
    if lines != bus:
        bad.append(('the bus', [(a, b) for a, b in zip(lines, bus) if a != b][:2],
                    len(lines), len(bus)))
    if [w[0] for w in m.fep.wire] != WIRE:
        bad.append(('the device', [w[0] for w in m.fep.wire]))
    if (m.scsi_commands, m.scsi_deferred, len(m.scsi_waiting)) != (9, 2, 0):
        bad.append(('commands, waited, waiting', m.scsi_commands, m.scsi_deferred,
                    len(m.scsi_waiting)))
    return bad


# ---- ref_scsi.py's IPL parts, as scripts (the reference alone, for now) ----
class Counted(list):
    """A trace that counts its lines and keeps the B, C and S lines."""

    def __init__(self):
        list.__init__(self)
        self.n = 0

    def append(self, ln):
        self.n += 1
        if ln[0] in 'BCS':
            list.append(self, ln)


def ipl_script(files, device):
    """ref_scsi.boot as a driver.Script: the body of ipl:boot0/0, its
    variables in slots 0..8; RUN, then POLL and RUN again while the
    device finishes a waiting command (Script.live)."""
    import lockstep_cons as cons
    import ref_scsi
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    P = lambda mod, p: pimm.predicate(im, mod, p)       # noqa: E731
    list_bytes = ref_scsi.listing(files)

    def make():
        m = pimm.Machine()
        opened = []

        def open_file(path):
            name = cons.ascii_of(struct.unpack('>%dH' % (len(path) // 2), path))
            opened.append(name)
            if name == ref_scsi.LIST:
                return list_bytes
            if name.startswith(ref_scsi.DIR):
                if name not in ref_scsi.FILES:
                    ref_scsi.FILES[name] = ref_scsi.words_bytes(
                        ref_scsi.lfile.file_words(name[len(ref_scsi.DIR):]))
                return ref_scsi.FILES[name]
            return None
        m.fep = fepm.Fep(open_file, **device)
        m.fep.opened = opened
        return m
    s = driver.Script()
    s.make = make
    var = ['Fep', 'GeneralTail', 'FileReq', 'ScsiEnd', 'OpenReqs', 'Files', 'Close', 'Loaded',
           'BootInfo']
    v = {k: i for i, k in enumerate(var)}
    for k in var:
        s.newvar(v[k])
    s.unifyc(v['GeneralTail'], I(0))

    def spawn(pc, args):
        for i, a in enumerate(args):
            if isinstance(a, int):
                s.arg(i + 1, a)
            else:
                s.argc(i + 1, a[1])
        s.spawn(pc, len(args))
    spawn(P('ipl', 'close/1'), [v['Close']])
    spawn(P('ipl_loader', 'load/4'), [v['Files'], v['OpenReqs'], v['Close'], v['Loaded']])
    s.string(9, 16, cons.jis(ref_scsi.LIST))
    spawn(P('ipl', 'ipl_files/4'), [v['FileReq'], 9, v['OpenReqs'], v['Files']])
    spawn(P('ipl_scsi', 'scsi/4'), [v['Fep'], v['GeneralTail'], v['FileReq'], v['ScsiEnd']])
    s.vector(10, 11, [(pimm.ATOM, names['normal']), ('slot', v['Fep'])])
    spawn(P('scsi_fep_module', 'create/7'), [('c', I(0)), ('c', I(0)), ('c', I(7)),
                                             ('c', I(0)), ('c', I(1)), ('c', I(0)), 10])
    spawn(P('ipl', 'make_boot_info/1'), [v['BootInfo']])
    return s, v


def ipl_build(n):
    """IPL part n (1..6, ref_scsi.PARTS' order) as a script, built live
    (Script.live): RUN, then POLL and RUN again while the device
    finishes a waiting command, then a POLL that finishes none (where
    the reference ran dry for good)."""
    import ref_scsi
    label, files, device = ref_scsi.PARTS[n - 1]
    s, v = ipl_script(files, device)
    s.ops.insert(0, ('label', label))
    s.run()
    polls = 0
    while True:
        m = s.live()
        if not m.scsi_waiting:
            break
        before = m.scsi_deferred - len(m.scsi_waiting)
        s.poll()
        m = s.live()
        if m.scsi_deferred - len(m.scsi_waiting) == before:
            break
        polls += 1
        s.run()
    s.polls = polls
    return s, v, label, files, device


def ipl_check(s, v, label, files, device, m, slot, trace):
    """ref_scsi.check, and the B lines against the device's record."""
    import ref_scsi
    m.polls = s.polls
    words = {k: slot[i] for k, i in v.items()}
    bad = ref_scsi.check(label, files, device, m, words, m.fep.opened)
    # a B line per device call, the finished ones as the device recorded them
    lines = [ln for ln in trace if ln.startswith('B ') and ln != 'B init']
    calls = [e for e in m.scsi_tape if not (e and e[0] == 'init')]
    done = [ln for ln, e in zip(lines, calls) if e is not None]
    wire = ['B 7 %d %s %d %d%s' % (cdb_[1] >> 5, cdb_.hex(), 1 if out else 2 if back else 0,
                                     len(out) or (cdb_[2] << 16 | cdb_[3] << 8 | cdb_[4]),
                                     ' ' + out.hex() if out else '')
            for name, cdb_, out, back in m.fep.wire]
    if len(lines) != len(calls) or done != wire:
        bad.append(('the bus', len(lines), len(calls),
                    [(a, b) for a, b in zip(done, wire) if a != b][:1]))
    return bad


def ipl_reference(n):
    """Part n on the reference alone, a counting trace."""
    s, v, label, files, device = ipl_build(n)
    t = time.time()
    m = s.make()
    m.tr = Counted()
    slot = [(0, 0)] * 16
    outs = []
    for o in s.ops:
        if o[0] != 'label':
            driver.Script._do(m, slot, o, outs, label)
    m.seconds = time.time() - t
    return ipl_check(s, v, label, files, device, m, slot, m.tr), m, s


def reference(argv):
    s, want, bus = script()
    parts = dict(s.play())
    bad = check(s, s.machine, want, bus, parts)
    print('direct: %r, %d parts, %d lines, %d goals left waiting'
          % (bad, len(parts), sum(len(p) for p in parts.values()), s.machine.nsusp))
    for n in range(1, 7):
        b, m, si = ipl_reference(n)
        print('%d %-12s %r: %d commands, %d B lines, %d trace lines, %d polls, %.0f s'
              % (n, si.ops[0][1], b, len(m.fep.wire), sum(1 for ln in m.tr if ln[0] == 'B'),
                 m.tr.n, si.polls, m.seconds))
        bad += b
    return 1 if bad else 0


def ipl_main(argv, n):
    s, v, label, files, device = ipl_build(n)
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1], tape=s.record_tape())
        return 0
    name = 'pimm lockstep scsi@%d (%s)' % (n, label)
    ok, m = driver.compare(s, sys.stdin, name, dict(parts=1, lines=PINNED_IPL[label]))
    if not ok:
        return 1
    bad = ipl_check(s, v, label, files, device, m, s.slots, m.tr)
    if bad:
        print('%s: FAIL %r' % (name, bad[:3]))
        return 1
    print("%s: PASS (ref_scsi.py's part on the Bluespec core: the IPL's own SCSI file "
          'service, the device on a tape; %d trace lines identical to the reference model, '
          '%d B lines, %d commands finished, %d polls; ref_scsi.py\'s checks)'
          % (name, s.counts['lines'], sum(1 for ln in m.tr if ln.startswith('B ')),
             len(m.fep.wire), s.polls))
    return 0


def main(argv):
    if '--reference' in argv:
        return reference(argv)
    if '--part' in argv:
        return ipl_main(argv, int(argv[argv.index('--part') + 1]))
    s, want, bus = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1], tape=s.record_tape())
        return 0
    kept = {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            yield what, lines
    s.play = keeping
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep scsi',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(s, m, want, bus, kept)
    if bad:
        print('pimm lockstep scsi: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep scsi: PASS (scsi_init and scsi_command on the Bluespec core, the '
          'device on a tape: %d parts, %d trace lines identical to the reference model, '
          '%d device calls (B lines) of %d commands compared byte for byte; scsi:create/2 and '
          'scsi:command_executer/2 at their sites: TEST UNIT READY, SEND, RECEIVE, a reply '
          'cut in two, two commands that waited (one finished inside a SEND, one at a '
          "poll), an element waited for; ref_scsi.py's IPL parts are scsi@1..6)"
          % (s.counts['parts'], s.counts['lines'], len(bus) - 1, m.scsi_commands))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
