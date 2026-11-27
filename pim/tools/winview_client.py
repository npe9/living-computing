#!/usr/bin/env python3
"""A stdlib client of tools/winview (docs/simpos/winview_protocol.md), OURS.

    python3 -I tools/winview_client.py SOCKET FRAME.pbm [SECONDS]

Sends H (the PBM's size) and F (its dots), then prints every event the
viewer sends for SECONDS (default 2) or until Q.  It is the protocol's
check (bsv/run_win_live.sh `viewer`) and the pattern for the software
window stack's client (psi/windev.py, a later agent's).
"""
import socket
import struct
import sys
import time


def read_pbm(path):
    data = open(path, 'rb').read()
    parts = data.split(b'\n', 2)
    assert parts[0] == b'P4', 'a P4 PBM'
    w, h = map(int, parts[1].split())
    return w, h, parts[2][:((w + 7) // 8) * h]


def msg(typ, payload):
    return typ.encode() + struct.pack('>I', len(payload)) + payload


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    w, h, rows = read_pbm(argv[1])
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(argv[0])
    s.sendall(msg('H', struct.pack('>HH', w, h) + b'winview_client'))
    s.sendall(msg('F', struct.pack('>HH', w, h) + rows))
    s.settimeout(0.2)
    end = time.time() + (float(argv[2]) if len(argv) > 2 else 2.0)
    buf = b''
    while time.time() < end:
        try:
            got = s.recv(4096)
        except socket.timeout:
            continue
        if not got:
            break
        buf += got
        while len(buf) >= 5:
            typ, n = chr(buf[0]), struct.unpack('>I', buf[1:5])[0]
            if len(buf) < 5 + n:
                break
            p, buf = buf[5:5 + n], buf[5 + n:]
            if typ == 'K':
                print('key %s %02x' % ('down' if p[0] else 'up', struct.unpack('>H', p[1:3])[0]))
            elif typ == 'M':
                print('move %d %d' % struct.unpack('>HH', p))
            elif typ == 'B':
                b, d, x, y = struct.unpack('>BBHH', p)
                print('button %s %s %d %d' % ('lmr'[b], 'down' if d else 'up', x, y))
            elif typ == 'Q':
                print('quit')
                return 0
            sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
