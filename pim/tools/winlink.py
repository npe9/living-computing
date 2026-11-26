#!/usr/bin/env python3
"""The window host link: framing, the board receiver's model, the checker.

docs/simpos/window_hardware_plan.md §3.4 and milestone H6 (its RTL half):
the link carries the box's drawing commands down and its answers up, over
the ULX3S's FTDI UART (8N1).  ALL OURS: the PSI had no such link (the
display was local to the CPU); this is the scaffolding that lets a host
running kl0 drive the board, and the frame format below is the contract
that bsv/WinLink.bsv (mkWinLink) implements.  bsv/run_win_link.sh runs the
RTL against this file.

DOWN, host to board, one box command a frame (psi/winfb.py's 104-bit
record, which this file reads with winfb.parse_stream):

    A5  SEQ  LEN  PAYLOAD[LEN]  CRC_HI  CRC_LO

  LEN is 13 (the record: the opcode byte, then operands A..F, each 16 bits
  big-endian).  SEQ counts frames mod 256 from 0.  CRC is CRC-16/CCITT-FALSE
  (polynomial 0x1021, initial 0xffff, no reflection, no final xor; its
  check value for b"123456789" is 0x29b1) over SEQ, LEN and the payload.

UP, board to host:

    5A  SEQ  TYPE  LEN  PAYLOAD[LEN]  CRC_HI  CRC_LO      (CRC over SEQ..payload)

  TYPE 0 status   LEN 1: the box's status for command SEQ (winfb.py's codes)
  TYPE 1 data     LEN 128: 64 frame words, big-endian, of command SEQ's dump
                  (1,280 records a dump, in frame order, then its status)
  TYPE 2 error    LEN 2: CODE, then the SEQ the receiver expected next
                  CODE 1 CRC: a frame's CRC was wrong; the frame is dropped
                  CODE 2 LEN: LEN was not 13; the frame is dropped
                  CODE 3 SEQ: a good frame out of sequence (a frame was
                         lost before it); it is reported, then drawn, and the
                         receiver expects its SEQ + 1 next
  TYPE 3 event    LEN 10: an input event record (H5/H7s, tools/wininput.py's
                  header: KIND, A, B, C, FLAGS, T); SEQ counts event records
                  mod 256.  Not an answer: a host's flow control counts only
                  TYPE 0 and TYPE 2 records.
  An error record is never placed inside another record.

THE RECEIVER (the board's; `receive` below is its model, byte for byte):
  hunt for A5; take SEQ and LEN; a LEN other than 13 is error 2, and the
  hunt resumes with the next byte; else take 13 payload bytes and the two
  CRC bytes; a wrong CRC is error 1 (the hunt resumes after the frame's
  last byte); a SEQ other than the expected is error 3; a good frame's
  command goes to the box, and the expected SEQ becomes its SEQ + 1.  A dropped byte thus costs
  the frame it was in (and, when the shortened frame swallowed the next
  frame's first bytes, that one too): a CRC error is reported, nothing of
  the bad frame is drawn, and the sequence check reports the loss of a
  frame whose bytes were all taken.

Use:
    python3 -I tools/winlink.py encode STREAM OUT.hex [--drop N] [--flip N]
        frames for STREAM's commands, then a dump (psi/winfb.py's `end`
        image); one byte a line, $readmemh-readable.  --drop N deletes
        byte N of the encoding, --flip N inverts bit 0 of byte N (the
        bench's injected line faults).
    python3 -I tools/winlink.py check IN.hex OUT.hex
        OUT.hex is what the bench read on the board's transmit line.  Its
        records must parse with good CRCs, its error records must be
        receive(IN)'s, its statuses those of psi/winfb.py run on the
        commands receive(IN) accepted, and each dump's 1,280 data records
        that run's frame at that dump.
    python3 -I tools/winlink.py selftest
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'psi'))
import winfb  # noqa: E402  (the drawing reference, read only)

SYNC_DOWN, SYNC_UP = 0xa5, 0x5a
LEN = 13
T_STATUS, T_DATA, T_ERROR, T_EVENT = 0, 1, 2, 3
E_CRC, E_LEN, E_SEQ = 1, 2, 3
WORDS_PER_DATA = 64


def crc16(data, crc=0xffff):
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xffff
    return crc


def record_bytes(op, a):
    out = [op]
    for v in a:
        out += [v >> 8, v & 0xff]
    return out


def frame(seq, payload):
    body = [seq & 0xff, len(payload)] + list(payload)
    c = crc16(body)
    return [SYNC_DOWN] + body + [c >> 8, c & 0xff]


def encode(text):
    """The down bytes for a stream: its commands, then the final dump."""
    out = []
    seq = 0
    for op, a in winfb.parse_stream(text):
        if op >> 4 == winfb.END:
            break
        out += frame(seq, record_bytes(op, a))
        seq += 1
    out += frame(seq, record_bytes(winfb.DUMP << 4, [0] * 6))
    return out


def receive(data):
    """The board receiver's model: (accepted [(seq, op, a)], errors [(code, expected)])."""
    acc, errs = [], []
    exp = 0
    i, n = 0, len(data)
    while i < n:
        if data[i] != SYNC_DOWN:
            i += 1
            continue
        if i + 2 >= n:
            break
        seq, ln = data[i + 1], data[i + 2]
        if ln != LEN:
            errs.append((E_LEN, exp))
            i += 3
            continue
        if i + 3 + LEN + 2 > n:
            break
        body = data[i + 1:i + 3 + LEN]
        c = (data[i + 3 + LEN] << 8) | data[i + 4 + LEN]
        i += 5 + LEN
        if crc16(body) != c:
            errs.append((E_CRC, exp))
            continue
        if seq != exp:
            errs.append((E_SEQ, exp))
        p = body[2:]
        a = [(p[1 + 2 * k] << 8) | p[2 + 2 * k] for k in range(6)]
        acc.append((seq, p[0], a))
        exp = (seq + 1) & 0xff
    return acc, errs


def parse_up(data):
    """Up records [(seq, type, payload)]; raises on a bad record."""
    out = []
    i, n = 0, len(data)
    while i < n:
        if data[i] != SYNC_UP:
            raise ValueError('byte %d: %02x where a record starts' % (i, data[i]))
        if i + 4 > n:
            raise ValueError('byte %d: a cut record' % i)
        seq, typ, ln = data[i + 1], data[i + 2], data[i + 3]
        if i + 4 + ln + 2 > n:
            raise ValueError('byte %d: a cut record' % i)
        body = data[i + 1:i + 4 + ln]
        c = (data[i + 4 + ln] << 8) | data[i + 5 + ln]
        if crc16(body) != c:
            raise ValueError('byte %d: record CRC %04x, computed %04x' % (i, c, crc16(body)))
        out.append((seq, typ, list(body[3:])))
        i += 6 + ln
    return out


def read_hex(path):
    out = []
    for line in open(path):
        line = line.split('//', 1)[0].strip()
        if line:
            out.append(int(line, 16))
    return out


def write_hex(path, data):
    with open(path, 'w') as f:
        for b in data:
            f.write('%02x\n' % b)


def check(inp, up):
    """'' when the board's answer is right, else what is wrong."""
    acc, errs = receive(inp)
    recs = parse_up(up)
    got_errs = [(p[0], p[1]) for s, t, p in recs if t == T_ERROR]
    if got_errs != errs:
        return 'error records %r, expected %r' % (got_errs, errs)
    stats = [(s, p[0]) for s, t, p in recs if t == T_STATUS]
    # the accepted commands through the reference
    fr = winfb.Frame(winfb.test_11())
    want = []
    for s, op, a in acc:
        want.append((s, fr.command(op, a)))
    if stats != want:
        return 'statuses %r, expected %r' % (stats[:8], want[:8])
    data = [p for s, t, p in recs if t == T_DATA]
    dumps = sum(1 for _, op, _a in acc if op >> 4 == winfb.DUMP)
    if len(data) != 1280 * dumps:
        return '%d data records for %d dumps' % (len(data), dumps)
    for k in range(dumps):
        img = bytes(b for p in data[1280 * k:1280 * (k + 1)] for b in p)
        if img != fr.dumps[k][-163840:]:
            return 'dump %d differs from psi/winfb.py\'s frame' % k
    return ''


def selftest():
    assert crc16(b'123456789') == 0x29b1
    s = winfb.assemble('fill 1 2 3 4 set\nline 0 0 9 9 1 0xffff xor\nend\n')
    d = encode(s)
    assert len(d) == 3 * 18
    acc, errs = receive(d)
    assert [x[0] for x in acc] == [0, 1, 2] and errs == []
    acc, errs = receive(d[:5] + d[6:])                   # a payload byte lost
    assert [x[0] for x in acc] == [2] and errs == [(E_CRC, 0), (E_SEQ, 0)], (acc, errs)
    f = list(d)
    f[18 + 2] = 12                                      # a bad LEN
    acc, errs = receive(f)
    assert [x[0] for x in acc] == [0, 2] and errs == [(E_LEN, 1), (E_SEQ, 1)], (acc, errs)
    print('winlink selftest: OK')


def main(argv):
    if len(argv) >= 3 and argv[0] == 'encode':
        d = encode(open(argv[1]).read())
        rest = argv[3:]
        while rest:
            opt, n = rest[0], int(rest[1], 0)
            rest = rest[2:]
            if opt == '--drop':
                del d[n]
            elif opt == '--flip':
                d[n] ^= 1
            else:
                raise SystemExit('unknown option %s' % opt)
        write_hex(argv[2], d)
        return 0
    if len(argv) == 3 and argv[0] == 'check':
        r = check(read_hex(argv[1]), read_hex(argv[2]))
        if r:
            print('winlink check: ' + r)
            return 1
        acc, errs = receive(read_hex(argv[1]))
        print('winlink check: %d commands accepted, %d link errors reported, '
              'statuses and the dump = psi/winfb.py' % (len(acc), len(errs)))
        return 0
    if argv == ['selftest']:
        selftest()
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
