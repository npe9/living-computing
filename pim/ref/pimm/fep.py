#!/usr/bin/env python3
"""A small model of the front-end processor (FEP) on the SCSI bus.

PROTOTYPE, for the reference model only (pimm.Machine.fep).  It is the
other end of the built-in scsi_command: a SCSI target of the
processor type at unit 7, which takes packets with SEND on LUN 0 and
gives them with RECEIVE on LUN 1, and answers the file requests the
IPL makes.  The real FEP (a PSI running pimfep.ptf) is not held as
source; this is written from the PIMOS side of the protocol:

  SCSI level     bios/scsi/scsi_common.kl1, scsi_processor.kl1
                 (TEST UNIT READY 00h, SEND 0Ah, RECEIVE 08h; group 0
                 CDBs; the length in bytes 2-4)
  packet level   the IPL image's scsi_fep_module (send_last_packet/9,
                 send_continued_packet/10, receive_packet*/9,
                 msg_to_str8/2, str8_to_msg*/n as decompiled by
                 asm/kl1decomp.py) and the kernel's
                 bios/fep_module/scsi_fep.kl1; laid out in
                 docs/binary_reverse_engineering.md 1.4
  commands       macro/pimos/pimos/pimos.vmac (fep#read_open 201,
                 fep#getb 210, fep#close 60, fep#abort 70; fep#normal
                 1, fep#eod 2, fep#abnormal 5)

OURS, each for want of the FEP's own code:
  - MAX_BUFFER, the packet buffer size scsi_init reports: 16000, the
    number in the stand-in bios/scsi/scsi_blt.kl1;
  - a reply is queued when the request's last packet arrives, and a
    RECEIVE with nothing queued is not answered (command() returns
    None; the caller holds it);
  - an open of a file that is not there is answered with status 5;
  - the unit of getb's count: `getb_unit` bytes per unit, 1 by
    default.  The IPL does not determine it; the kernel's file
    device asks for Size*2+1 (server/fep/file/file_dvcb.kl1:
    getb(Size)), and counted in bytes every reply is odd, widened by a
    zero byte, the data a byte late (pimos.conf read as with_console,
    then end_of_file): longrun_ipl.py gives the kernel 2, the count in
    16-bit characters, READ from pimfep##pimos_file getb/4 @259-263
    (new_string(S, Size, 16), docs/fep_services.md 2.2); the default 1
    is kept for the IPL, which works either way.
    docs/binary_reverse_engineering.md 1.4;
  - a getb at the end of the data is answered with status 2 every
    time it is asked (the loader asks more than once);
  - a reply longer than the RECEIVE's length is cut into continued
    packets as the IPL cuts its own (flag 1 on all but the last).
    The IPL does not then ask for the rest (ref_scsi.py, "small
    buffer"), so in practice a reply must fit;
  - close is answered with status 1;
  - append_open (203) is accepted, the bytes appended kept in
    Fep.appended (OURS; the kernel's syslog, Fep.request);
  - create_timer (310) is accepted (OURS, Fep.request),
    get_date_time (304) answered with a fixed date and the machine's
    clock as the time of day (DATE, Fep.ticks), and the timer's close
    (60) accepted;
  - from fep_attributes (240) on, the kernel's start and a local
    login as docs/fep_services.md 6 and 7 lay them out (2026-11-24):
    240, the string-I/O programs (601, 620), the window calls, close
    (60) on every kind, a request the FEP holds (the login server's
    io(1), a window's getl) answered by an event the bench asks for
    when the machine is idle (Fep.idle: the scripted login of 7.5,
    then the lines typed, Fep(lines=..): each the answer
    [1, the line in JIS] to the next held getl, in order, with no
    newline (whether the FEP sends one is not known, 7.5; the shell
    took "shutdown" without one); the event list is OURS, its reply's form is
    bios/fep_module/win_dvc.kl1:307-312), and abort (70) answering a held request with status 6 (6.7).
    Each answer's marks (SOURCED, READ, HELD FILE, OURS) are at its
    constant below;
  - (2026-11-25, R7) pathname (221) and attributes (222) on a read
    file that open_file gave as a FileData (a home file,
    longrun_ipl.home_file): [1, its pathname in JIS] and [1, its
    attribute string] (attribute_string: the format PIMOS reads,
    server/fep/file/file_dvcb.kl1:598-691; the values the caller's,
    OURS).  On a file given as plain bytes neither is served (FepError,
    as before).  jis() writes a newline as 00 0A, as the held text
    files hold it (object/pimos.conf);
  - the kernel's bus scan (bios/boot/scsi_man.kl1): INQUIRY to unit 7
    is answered with five bytes, 03 00 07 00 00 (the values of the
    source's own canned answer, the length ours), and TEST UNIT READY
    to a unit with no device, 0-5, with Result = completion code 8
    (no_status), NO_DEVICE: a choice about the lost built-in, not the
    FEP (Fep.command cites the source).
Anything else (another unit or LUN, another CDB, another command)
raises FepError: nothing is guessed.

The kernel's FEP conversation (rung S0 of docs/scsi_plan.md;
longrun_ipl.py --reference --go --fep, or --load FILE --go --fep), as
far as it goes (2026-11-24): TEST UNIT READY and INQUIRY to unit 7,
then TEST UNIT READY to units 5, 4, 3, 2, 1, 0, then the kernel's
first FEP message, append_open of pimos:pimos.syslog (accepted;
docs/binary_reverse_engineering.md 1.4, "The kernel's FEP
conversation").
"""
import struct

TEST_UNIT_READY, RECEIVE, SEND, INQUIRY = 0x00, 0x08, 0x0a, 0x12
READ_OPEN, APPEND_OPEN, GETB, CLOSE, ABORT, TERMINATE = 201, 203, 210, 60, 70, 80
PATHNAME, ATTRIBUTES_OF = 221, 222   # pimos.vmac:77 fep#pathname, :138 fep#attributes
CREATE_TIMER = 310                 # pimos.vmac:146 fep#create_timer
# docs/fep_services.md 2 (the commands, from pimos.vmac):
FEP_ATTRIBUTES, CREATE_STRING_IO, IO = 240, 601, 620
CREATE_WINDOW, GETL, PUTB, FLUSH = 104, 110, 111, 112
WINDOW_ANSWERED = (126, 127, 130, 132, 141, 142, 143, PUTB, FLUSH)  # reshape_by_mouse,
# reshape, set_title, set_font, activate, deactivate, show, putb, flush:
# {Id, 1} (fep_services.md 6.8, READ for 127, 132, 143; 7.5).  126
# (2026-11-24, the listener's window): {Id, 1} is PIMOS's form
# (bios/fep_module/win_dvc.kl1:357-363); the PSI's handler is
# pimos_window_editor reshape_by_mouse/3 (fep_services.md 6.2), its
# answer taken to be the class's {Id, 1} as 6.8 reads for the three
# (INFERENCE); where the operator puts the window with the mouse is
# not a value PIMOS is told
ABORTED = 6                        # fep#aborted (pimos.vmac)
# Text as the PSI keeps it: 16-bit JIS X 0208, two bytes a character,
# the high byte first (fep_services.md 7.5): the letters and digits in
# row 23, the punctuation of asm/psdpim.py's table in row 21
_PUNCT = {' ': 0x21, ',': 0x24, '.': 0x25, ':': 0x27, '_': 0x32, '/': 0x3f,
          '-': 0x5d, '<': 0x63, '>': 0x64, '!': 0x2a, '?': 0x29, '*': 0x76,
          # PIMOS's own table, server/telnet/code_cv.kl1:152-251
          # (table_ascii_to_jis): for a typed command line's quotes,
          # brackets and the shell's <= and =>, and (2026-11-24) the
          # rest of its printable ASCII, for the commands of
          # lockstep_shell.py's APPS
          '"': 0x49, '(': 0x4a, ')': 0x4b, '=': 0x61,
          '#': 0x74, '$': 0x70, '%': 0x73, '&': 0x75, "'": 0x47, '+': 0x5c,
          ';': 0x28, '@': 0x77, '[': 0x4e, '\\': 0x40, ']': 0x4f, '^': 0x30,
          '`': 0x46, '{': 0x50, '|': 0x43, '}': 0x51, '~': 0x41}


def jis(text):
    out = b''
    for ch in text:
        out += b'\x00\x0a' if ch == '\n' else bytes([0x23, ord(ch)]) if ch.isalnum() \
            else bytes([0x21, _PUNCT[ch]])
    return out


def unjis(data):
    """16-bit JIS bytes as text (another code as <hex>)."""
    back = {v: k for k, v in _PUNCT.items()}
    out = ''
    for i in range(0, len(data) - 1, 2):
        hi, lo = data[i], data[i + 1]
        out += chr(lo) if hi == 0x23 else back[lo] if hi == 0x21 and lo in back \
            else '\n' if (hi, lo) == (0, 10) else '<%02x%02x>' % (hi, lo)
    return out


# 240's answer {Id, 1, Code, OS, Host, FepVer, Dir, FileVer, Comment},
# as the PSI's refute_server_command/3 makes it (fep_services.md 6.3):
# Code 0 (fep#jiskanji), FepVer "V0.45", Dir ">" (the path delimiter,
# 7.8), FileVer ".", Comment "" READ FROM CONSTANTS; OS is "SIMPOS "
# ++ SIMPOS's version and Host the node name, neither held: "V7" and
# "PSI" are OURS
ATTRIBUTES = [0, jis('SIMPOS V7'), jis('PSI'), jis('V0.45'), jis('>'), jis('.'), b'']
# the string-I/O programs 601 makes (fep_services.md 6.4)
REPLIER, SERVER, USER_DEVICE = ('pimos_remote_login_replier', 'pimos_remote_login_server',
                                'simpos_user_device')
# the string-I/O window PIMOS opens for shutdown_body's third branch
# (server/user/shutdown_b.kl1:39-53; also pass_body.kl1:68,
# su_body.kl1:51): its io/4 takes window codes (fep_services.md 2.6,
# 6.4), PSI side, not held
STD_WINDOW = 'pimos_standard_io_window'
# The scripted login (fep_services.md 7.5): Node "local" (SOURCED,
# login.kl1:1256), RN "pmpsi" and RP "" (OURS; the name HELD in
# login.com), UN "pimos" and UP "" (HELD FILE, pimos.logins), the ID 0
# (READ: the smallest integer from 0 not a key of the replier's socket
# table, pimfep##pimos_remote_login_socket_table get_key/2 @a8-b2,
# get_key/4 @b7-cf; fep_services.md 6.5)
LOGIN = dict(id=0, node='local', rn='pmpsi', rp='', un='pimos', up='')


def login_record(id, node, rn, rp, un, up):
    """NI, the answer to the server's held io(1): [ID, the lengths of
    Node, RN, RP, UN, UP] then the five strings, 16-bit elements
    (fep_services.md 6.5, 7.5; login.kl1 get_node_info/3)."""
    strs = [node, rn, rp, un, up]
    head = b''.join(n.to_bytes(2, 'big') for n in [id] + [len(x) for x in strs])
    return head + b''.join(jis(x) for x in strs)


GET_DATE_TIME = 304                # pimos.vmac:95 fep#get_date_time
# the FEP's clock, OURS, the same on every run.  The date the
# banner's, 20-May-1993, as PIMOS counts dates (days from 01-Jan-1901:
# utility/timer/date.kl1 get_date_count, check_input); the time of
# day (milliseconds from midnight: utility/timer/time.kl1
# get_time_count) follows the machine's clock (pimm.py timer(), set
# into Fep.ticks before each command, 1/16 msec), so midnight is the
# moment the processor booted (2026-11-24; it was a fixed 0).  PIMOS
# takes the difference of the two as its time equation (server/fep/
# fep/time_sv.kl1 wait_date_time/2, compare/4)
DATE = 33742
NORMAL, EOD, ABNORMAL = 1, 2, 5
# scsi_command's Result for a unit with no device (OURS, Fep.command)
NO_DEVICE = 8 << 8


class FepError(Exception):
    pass


class FileData(bytes):
    """A file's bytes, as open_file returns them, with what 221
    (pathname) and 222 (attributes) answer for it: a home file
    (longrun_ipl.home_file; docs/fep_services.md 2.2).  A file given as
    plain bytes (the held pimos: set) has neither, and 221 or 222 on it
    raises FepError, as any request not served does."""

    def __new__(cls, data, pathname, attributes):
        o = bytes.__new__(cls, data)
        o.pathname, o.attributes = pathname, attributes
        return o


def attribute_string(owner, update_user, cdate, ctime, mdate, mtime, links, fsize, rsize):
    """222's answer, the one string PIMOS reads: Owner, UpdateUser,
    CDate, CTime, MDate, MTime, then LinkCnt, FSize, RSize in decimal,
    each field ended by an LF (16-bit JIS, element 10), the integers'
    LF needed (server/fep/file/file_dvcb.kl1:598-691, attributes/2,
    get_data/7, if_lf/8, attributes_int/6: an integer's digits are
    counted to one before its LF, and the string must end at the last
    LF; docs/fep_services.md U7).  A date is DD-Mon-YY and a time
    HH:MM:SS (library/utility/fileutil.kl1:31-58 normalize_date_time,
    the substrings it takes), what the compiler reads (library/loader/
    dstrbt.kl1 distribute/5)."""
    fields = [owner, update_user, cdate, ctime, mdate, mtime] + ['%d' % n for n in
                                                                (links, fsize, rsize)]
    return jis(''.join(f + '\n' for f in fields))


def pack_message(args):
    """The body of a packet after the 8-byte header: command or status,
    the number of arguments, a length word for each (-1 for an
    integer), then the arguments, a string padded with zeros to four
    bytes.  args[0] is the command or status."""
    rest = args[1:]
    out = struct.pack('>ii', args[0], len(rest))
    for a in rest:
        out += struct.pack('>i', -1 if isinstance(a, int) else len(a))
    for a in rest:
        out += struct.pack('>i', a) if isinstance(a, int) else a + bytes(-len(a) % 4)
    return out


def unpack_message(body):
    """The inverse of pack_message: [command, argument, ...]."""
    cmd, n = struct.unpack('>ii', body[:8])
    lens = struct.unpack('>%di' % n, body[8:8 + 4 * n])
    at, out = 8 + 4 * n, [cmd]
    for ln in lens:
        if ln == -1:
            out.append(struct.unpack('>i', body[at:at + 4])[0])
            at += 4
        else:
            out.append(body[at:at + ln])
            at += ln + (-ln % 4)
    if at != len(body):
        raise FepError('a message of %d bytes, %d used' % (len(body), at))
    return out


class Fep:
    MAX_BUFFER = 16000
    UNIT, SEND_LUN, RECEIVE_LUN = 7, 0, 1
    # the units of the bus with nothing on them: all but the FEP's 7 and
    # PIM/m's own 6 (scsi_where's answer)
    ABSENT = (0, 1, 2, 3, 4, 5)

    def __init__(self, open_file, getb_unit=1, limit=None, max_buffer=None, lag=False,
                 getb_bytes=None, lines=()):
        """open_file(path bytes) -> the file's bytes, or None.  For
        tests: limit, the number of commands after which the device
        stops answering; max_buffer, another buffer size; lag, every
        RECEIVE is refused once before it is answered (a reply that
        is not ready when it is asked for); getb_bytes, the bytes a
        getb gives whatever it asks for; lines, the lines typed after
        the login, one per held getl (110), in order (OURS, the event
        list: fep_services.md 7.5)."""
        self.open_file = open_file
        self.getb_unit = getb_unit
        self.limit = limit
        self.lag = lag
        self.lagged = False
        self.getb_bytes = getb_bytes
        if max_buffer is not None:
            self.MAX_BUFFER = max_buffer
        self.wire = []          # (name, CDB, bytes out, bytes in) per finished command
        self.messages = []      # ('>' or '<', device id, [command or status, args...])
        self.partial = {}       # device id -> the pieces of a continued message
        self.files = {}         # device id -> [bytes, position]
        self.appending = {}     # device id -> the path it appends to
        self.timers = set()     # device ids of timers made
        self.strio = {}         # device id -> the string-I/O program's name (601)
        self.windows = set()    # device ids of windows made (104)
        self.listening = set()  # login server devices whose io(0, "local") was answered
        self.held = {}          # device id -> 'login' or 'getl': a request the FEP holds
        # the events Fep.idle takes, in order (OURS): the login, then
        # each line typed, the answer to the next held getl
        self.script = [('login', LOGIN)] + [('getl', line) for line in lines]
        self.log = []           # (device id, text): the replier's texts, a window's putb
        self.ticks = 0          # the machine's clock (1/16 msec), set by pimm.py
        self.appended = {}      # path -> the bytes appended to it (OURS)
        self.terminated = False  # {-1, 80} received: the link closed
        self.replies = []       # packets to give, in order
        self.stopped = False

    def known(self, dev):
        return (dev in self.files or dev in self.appending or dev in self.timers
                or dev in self.strio or dev in self.windows)

    def string_io(self, dev, name, command, data):
        """620 io(Command, Data) on a string-I/O device (fep_services.md
        6.4, 6.10, 7.5)."""
        if name == REPLIER and command in (0, 2):
            return [NORMAL, b'']
        if name == REPLIER and command == 1:
            # a text for the user; its element 0 is the login's ID.  The
            # PSI answers one character, 0 when it was sent (6.4)
            self.log.append((dev, unjis(data[2:])))
            return [NORMAL, bytes(2)]
        if name == SERVER and command == 0:
            kind = unjis(data)
            if kind == 'local':
                self.listening.add(dev)
                return [NORMAL, b'']
            if kind == 'tcpip':
                # no network here (fep_services.md 7.5, OURS): PIMOS
                # shows CANNOT MAKE A TCPIP LOGIN SERVICE!! and goes on
                return [ABNORMAL]
        if name == SERVER and command == 1 and dev in self.listening:
            # waits for a login: held (fep_services.md 7.3 row 1)
            self.held[dev] = 'login'
            return None
        if name == STD_WINDOW and command in (104, 130, 141, 111):
            # 104 its place and size ({324, 328, 40, 6} from
            # shutdown_b.kl1:43-47), 130 its title, 141 activate, 111
            # putb: [1, ""], OURS (the PSI's class is not held; the
            # window device's own 104/130/141/111 answer {Id, 1},
            # fep_services.md 2.6, and 620's reply carries a string,
            # 6.4).  A 111's text goes to the log
            if command == 111:
                self.log.append((dev, unjis(data)))
            return [NORMAL, b'']
        if name == STD_WINDOW and command == 110:
            # getl: held, as the window's 110, until the next typed line
            # (Fep.idle answers it [1, LINE], the form of 620's reply)
            self.held[dev] = 'getl'
            return None
        if name == USER_DEVICE and command == 0:
            # [len Name, len Pass] ++ Name ++ Pass: the user's home,
            # ">sys>user>" ++ Name, PIMOS's own default (SOURCED,
            # login_p.kl1:63; fep_services.md 7.5)
            n = int.from_bytes(data[:2], 'big')
            return [NORMAL, jis('>sys>user>') + data[4:4 + 2 * n]]
        raise FepError('device %d: io(%r, %r) on %s' % (dev, command, data, name))

    def command(self, unit, lun, cdb, length, direction, data):
        """One scsi_command.  Returns (result, bytes received), or None
        when the command cannot finish yet."""
        if self.limit is not None and len(self.wire) >= self.limit:
            self.stopped = True
            return None
        if unit in self.ABSENT and len(cdb) == 5 and cdb[0] == TEST_UNIT_READY \
                and direction == 0 and length == 0:
            # no device at this unit: the lost built-in's answer, not the
            # FEP's.  OURS: Result = completion code 8, status byte 0,
            # detail 0, which PIMOS reads as abnormal(no_status(8, 0))
            # (bios/scsi/scsi_common.kl1:186-199,
            # check_completion_code/4: completion-code bit 3 is the only
            # failure code the source names); the bus scan then drops
            # the unit without a message (bios/boot/scsi_man.kl1,
            # inquiry/8's last clause, SCSI = []), as the manual's boot
            # log has only unit 7 found (PIMOS manual e-sysman.tex:
            # 103-112, "SCSI UNITS FOUND" then 7 and 0)
            self.wire.append(('TEST UNIT READY, no device', cdb, b'', b''))
            return NO_DEVICE, b''
        if unit != self.UNIT or len(cdb) != 5:
            raise FepError('unit %d, CDB %s' % (unit, cdb.hex()))
        op, clun = cdb[0], cdb[1] >> 5
        clen = cdb[2] << 16 | cdb[3] << 8 | cdb[4]
        if clun != lun or cdb[1] & 31:
            raise FepError('LUN %d, CDB %s' % (lun, cdb.hex()))
        if op == TEST_UNIT_READY and direction == 0 and length == 0 and clen == 0:
            self.wire.append(('TEST UNIT READY', cdb, b'', b''))
            return 0, b''
        if op == INQUIRY and lun == 0 and direction == 2 and clen == length == 255:
            # the kernel's bus scan (bios/boot/scsi_man.kl1 inquiry/8,
            # bios/scsi/scsi_common.kl1:60-70, 255 = scsi#inquiry_data_
            # max, macro/pimos/scsi/scsi.vmac:42).  The bytes: device
            # type 3, processor (scsi.vmac:82; scsi_man.kl1 device_type/2
            # makes it `processor`), byte 1 0 (not removable), byte 2 7,
            # additional length 0: the values of the source's own canned
            # answer for a front end it does not ask, normal(scsi#
            # processor, 0, 7, "") (scsi_man.kl1, inquiry/8 under
            # fep_interface kl1_network).  Five bytes: OURS, the least
            # that gives that answer (check_inquiry_command/4's
            # `Length =:= 5` clause, scsi_common.kl1:99-106).  The FEP's
            # packages hold no inquiry answer to copy: no symbol or
            # literal of the kind in pimscsi.ptf's scsi_device,
            # scsi_handler, pseudo_scsi, scsi_communicator,
            # scsi_device_bus_management (asm/ptfdump.py; `sense` only)
            # nor in pimfep.ptf (an inquiry answer is the target's SCSI
            # controller's, presumably, not ESP code: INFERENCE)
            out = bytes([3, 0, 7, 0, 0])
            self.wire.append(('INQUIRY', cdb, b'', out))
            return 0, out
        if op == SEND and lun == self.SEND_LUN and direction == 1 and clen == length:
            self.wire.append(('SEND', cdb, data, b''))
            self.packet(data)
            return 0, b''
        if op == RECEIVE and lun == self.RECEIVE_LUN and direction == 2 and clen == length:
            if not self.replies:
                return None
            if self.lag and not self.lagged:
                self.lagged = True
                return None
            self.lagged = False
            if len(self.replies[0]) > length:
                # cut: this piece is continued, the rest keeps the header
                p = self.replies[0]
                self.replies[0] = p[:4] + struct.pack('>i', 1) + p[8:length]
                self.replies.insert(1, p[:8] + p[length:])
            out = self.replies.pop(0)
            self.wire.append(('RECEIVE', cdb, b'', out))
            return 0, out
        raise FepError('command %s on LUN %d, direction %d, length %d'
                       % (cdb.hex(), lun, direction, length))

    def answer(self, dev, reply):
        """Queue a reply packet for the device."""
        self.messages.append(('<', dev, reply))
        self.replies.append(struct.pack('>ii', dev, 0) + pack_message(reply))

    def idle(self):
        """The bench's question when the machine has nothing to run and
        no SCSI command finishes (fep_services.md 7.5, 7.7 item 1): the
        next scripted event answers a held request.  True if a reply
        was queued.  OURS: the idle test and the script."""
        if not self.script:
            return False
        kind, what = self.script[0]
        for dev, k in sorted(self.held.items()):
            if k == kind == 'login':
                self.script.pop(0)
                del self.held[dev]
                self.answer(dev, [NORMAL, login_record(**what)])
                return True
            if k == kind == 'getl':
                self.script.pop(0)
                del self.held[dev]
                self.answer(dev, [NORMAL, jis(what)])
                return True
        return False

    def packet(self, data):
        if len(data) < 8:
            raise FepError('a packet of %d bytes' % len(data))
        dev, flag = struct.unpack('>ii', data[:8])
        self.partial.setdefault(dev, []).append(data[8:])
        if flag == 1:
            return
        if flag != 0:
            raise FepError('packet flag %d' % flag)
        msg = unpack_message(b''.join(self.partial.pop(dev)))
        self.messages.append(('>', dev, msg))
        reply = self.request(dev, msg)
        if reply is not None:
            self.answer(dev, reply)

    def request(self, dev, msg):
        cmd = msg[0]
        if cmd == READ_OPEN and len(msg) == 5 and dev not in self.files:
            # {Id, 201, "", User, Password, Path}
            data = self.open_file(msg[4])
            if data is None:
                return [ABNORMAL]
            self.files[dev] = [data, 0]
            return [NORMAL]
        if cmd == PATHNAME and len(msg) == 1 and dev in self.files \
                and isinstance(self.files[dev][0], FileData):
            # {Id, 221}: {Id, 1, Pathname} (bios/fep_module/file_dvc.kl1:
            # 319; server/fep/file/file_dvcb.kl1 pathname/3 widens it to
            # 16 bits for Code 0).  The name is the home file's
            # (longrun_ipl.home_file)
            return [NORMAL, jis(self.files[dev][0].pathname)]
        if cmd == ATTRIBUTES_OF and len(msg) == 1 and dev in self.files \
                and isinstance(self.files[dev][0], FileData):
            # {Id, 222}: {Id, 1, Attributes}, one string (attribute_string;
            # file_dvc.kl1:324).  Read under Code 0 only because 240's
            # OS begins "SIMPOS" (file_dvcb.kl1 attributes0/4)
            return [NORMAL, self.files[dev][0].attributes]
        if cmd == APPEND_OPEN and len(msg) == 5 and dev not in self.files \
                and dev not in self.appending:
            # {Id, 203, "", User, Password, Path}: fep#append_open
            # (macro/pimos/pimos/pimos.vmac:69; bios/fep_module/
            # file_dvc.kl1 device_create/5, the reply as read_open's).
            # The kernel's syslog (bios/boot/syslog.kl1 wait_status1/3)
            # opens pimos:pimos.syslog so on every boot; a real FEP
            # appends to that file.  Accepted, OURS: the stand-in keeps
            # what is appended in memory (Fep.appended), so the boot
            # goes the way it does with a FEP that holds the file (an
            # ABNORMAL answer is also taken by PIMOS, with "SYSLOG
            # ERROR: reason / cannot open file pimos:pimos.syslog" on
            # the console).
            self.appending[dev] = msg[4]
            self.appended.setdefault(msg[4], bytearray())
            return [NORMAL]
        if cmd == CREATE_TIMER and len(msg) == 4 and dev not in self.timers:
            # {Id, 310, Node, User, Password}: fep#create_timer
            # (bios/fep_module/time_dvc.kl1 device_create/5; reply/9
            # takes [normal(Value)|_] with fep#normal in Value and goes
            # on to device_process, the timer's requests).  Accepted,
            # OURS: a FEP that has a timer.  ABNORMAL would also be
            # taken (the timer device ends, its stream answered with the
            # status)
            self.timers.add(dev)
            return [NORMAL]
        if cmd == FEP_ATTRIBUTES and len(msg) == 2 and not self.known(dev):
            # {Id, 240, Node}: the device ends with the reply, no close
            # (fep_services.md 2.2, 6.3)
            return [NORMAL] + ATTRIBUTES
        if cmd == CREATE_STRING_IO and len(msg) == 5 and not self.known(dev):
            # {C, 601, Node, User, Password, Name}: an object of the
            # program named (fep_services.md 6.4); the three a login
            # uses
            name = unjis(msg[4])
            if name not in (REPLIER, SERVER, USER_DEVICE, STD_WINDOW):
                raise FepError('device %d: create_string_io of %r' % (dev, name))
            self.strio[dev] = name
            return [NORMAL]
        if cmd == IO and len(msg) == 3 and dev in self.strio and dev not in self.held:
            return self.string_io(dev, self.strio[dev], msg[1], msg[2])
        if cmd == CREATE_WINDOW and len(msg) == 4 and not self.known(dev):
            # {W, 104, Node, User, Password} (fep_services.md 7.3 row 7)
            self.windows.add(dev)
            return [NORMAL]
        if cmd in WINDOW_ANSWERED and dev in self.windows and dev not in self.held:
            if cmd == PUTB:
                self.log.append((dev, unjis(msg[1])))
            return [NORMAL]
        if cmd == GETL and dev in self.windows and dev not in self.held:
            # held until a scripted line (fep_services.md 7.5)
            self.held[dev] = 'getl'
            return None
        if cmd == CLOSE and len(msg) == 1 and (dev in self.strio or dev in self.windows):
            # fep_services.md 6.10: one reply [1]
            self.strio.pop(dev, None)
            self.windows.discard(dev)
            self.listening.discard(dev)
            return [NORMAL]
        if cmd == ABORT and len(msg) == 1 and dev in self.held:
            # no reply to the 70; the request it interrupts gets 6
            # (fep_services.md 6.7)
            del self.held[dev]
            return [ABORTED]
        if cmd == GET_DATE_TIME and len(msg) == 1 and dev in self.timers:
            # {Id, 304}: the reply {Status, Date, Time}
            # (bios/fep_module/time_dvc.kl1 device_io1/13)
            return [NORMAL, DATE, (self.ticks // 16) % 86400000]
        if cmd == GETB and len(msg) == 2 and dev in self.files:
            f = self.files[dev]
            chunk = f[0][f[1]:f[1] + (self.getb_bytes or msg[1] * self.getb_unit)]
            if not chunk:
                return [EOD]
            f[1] += len(chunk)
            return [NORMAL, chunk]
        if cmd == CLOSE and len(msg) == 1 and dev in self.timers:
            # {Id, 60}: the timer device's end (bios/fep_module/
            # time_dvc.kl1 device_io1/13 at the stream's end, then
            # device_terminate/5: normal goes on to read the reply).
            # Accepted, OURS, as a file's close
            self.timers.discard(dev)
            return [NORMAL]
        if cmd == FLUSH and len(msg) == 1 and dev in self.files:
            # {Id, 112} on a file read-opened: {Id, 1} (bios/fep_module/
            # file_dvc.kl1:314; docs/fep_services.md 2.2, 6.2: the
            # PSI's pimos_file flush/3).  PIMOS flushes pimos.conf
            # after its last getb
            return [NORMAL]
        if cmd == CLOSE and len(msg) == 1 and dev in self.files:
            del self.files[dev]
            return [NORMAL]
        if cmd == CLOSE and len(msg) == 1 and dev in self.appending:
            # {Id, 60} on the file append-opened (the syslog's, at
            # PIMOS's end after a shutdown): a file's close, as a read
            # file's (bios/fep_module/file_dvc.kl1 device_terminate;
            # fep_services.md 2.2).  What was appended stays in
            # Fep.appended
            del self.appending[dev]
            return [NORMAL]
        if cmd == TERMINATE and len(msg) == 1 and dev == -1:
            # {-1, 80}, fep#terminate: sent when the link's stream
            # closes, at PIMOS's end; no reply is read
            # (bios/fep_module/scsi_fep.kl1:234; fep_services.md 1,
            # 2.1).  Noted, not answered
            self.terminated = True
            return None
        if cmd == ABORT and len(msg) == 1:
            return None
        raise FepError('device %d: request %r' % (dev, msg))


def hexdump(b, width=4):
    """Bytes as groups of `width`, in hex."""
    return ' '.join(b[i:i + width].hex() for i in range(0, len(b), width))
