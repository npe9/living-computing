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
    device counts bytes (server/fep/file/file_dvcb.kl1: getb(Size)
    asks for Size*2+1).  docs/binary_reverse_engineering.md 1.4;
  - a getb at the end of the data is answered with status 2 every
    time it is asked (the loader asks more than once);
  - a reply longer than the RECEIVE's length is cut into continued
    packets as the IPL cuts its own (flag 1 on all but the last).
    The IPL does not then ask for the rest (ref_scsi.py, "small
    buffer"), so in practice a reply must fit;
  - close is answered with status 1;
  - append_open (203) is accepted, the bytes appended kept in
    Fep.appended (OURS; the kernel's syslog, Fep.request);
  - create_timer (310) is accepted (OURS, Fep.request), and
    get_date_time (304) answered with a fixed clock (DATE, TIME);
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
READ_OPEN, APPEND_OPEN, GETB, CLOSE, ABORT = 201, 203, 210, 60, 70
CREATE_TIMER = 310                 # pimos.vmac:146 fep#create_timer
GET_DATE_TIME = 304                # pimos.vmac:95 fep#get_date_time
# the FEP's clock, OURS: fixed, so every run is the same.  The date
# the banner's, 20-May-1993, as PIMOS counts dates (days from
# 01-Jan-1901: utility/timer/date.kl1 get_date_count, check_input),
# the time 00:00:00 (milliseconds from midnight: utility/timer/
# time.kl1 get_time_count)
DATE, TIME = 33742, 0
NORMAL, EOD, ABNORMAL = 1, 2, 5
# scsi_command's Result for a unit with no device (OURS, Fep.command)
NO_DEVICE = 8 << 8


class FepError(Exception):
    pass


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
                 getb_bytes=None):
        """open_file(path bytes) -> the file's bytes, or None.  For
        tests: limit, the number of commands after which the device
        stops answering; max_buffer, another buffer size; lag, every
        RECEIVE is refused once before it is answered (a reply that
        is not ready when it is asked for); getb_bytes, the bytes a
        getb gives whatever it asks for."""
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
        self.appended = {}      # path -> the bytes appended to it (OURS)
        self.replies = []       # packets to give, in order
        self.stopped = False

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
            self.messages.append(('<', dev, reply))
            self.replies.append(struct.pack('>ii', dev, 0) + pack_message(reply))

    def request(self, dev, msg):
        cmd = msg[0]
        if cmd == READ_OPEN and len(msg) == 5 and dev not in self.files:
            # {Id, 201, "", User, Password, Path}
            data = self.open_file(msg[4])
            if data is None:
                return [ABNORMAL]
            self.files[dev] = [data, 0]
            return [NORMAL]
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
        if cmd == GET_DATE_TIME and len(msg) == 1 and dev in self.timers:
            # {Id, 304}: the reply {Status, Date, Time}
            # (bios/fep_module/time_dvc.kl1 device_io1/13)
            return [NORMAL, DATE, TIME]
        if cmd == GETB and len(msg) == 2 and dev in self.files:
            f = self.files[dev]
            chunk = f[0][f[1]:f[1] + (self.getb_bytes or msg[1] * self.getb_unit)]
            if not chunk:
                return [EOD]
            f[1] += len(chunk)
            return [NORMAL, chunk]
        if cmd == CLOSE and len(msg) == 1 and dev in self.files:
            del self.files[dev]
            return [NORMAL]
        if cmd == ABORT and len(msg) == 1:
            return None
        raise FepError('device %d: request %r' % (dev, msg))


def hexdump(b, width=4):
    """Bytes as groups of `width`, in hex."""
    return ' '.join(b[i:i + width].hex() for i in range(0, len(b), width))
