#!/usr/bin/env python3
"""Tests for the ULX3S ESP32 Ethernet relay (docs/ulx3s_ethernet.md).

Run from anywhere (needs a host C compiler, `cc`):

    python3 hobbit/tests/test_ethrelay.py

What is under test
------------------
`fpga/esp32_ethrelay/main/relay.c` is the firmware's link protocol (COBS
packets with a CRC-32, relay.h).  It is compiled here into
`fpga/esp32_ethrelay/host/relay_host.c`, the same relay with POSIX in
place of ESP-IDF: stdin/stdout stand for the UART to the FPGA, paced at
the UART's byte rate, and a UDP socket stands for WiFi.  The relay is
attached to a real `tools/qemu1e/hub.py` Hub, and a second hub port
stands for the 1e file server.  So the frames cross the hub's own framing
(one raw frame per datagram), and the link bytes are compared with an
independent encoder and decoder written here in Python (zlib's CRC-32).

Not under test: the ESP-IDF glue (`main/main.c`: WiFi, the UART driver,
the two tasks), which has not been compiled for the target (no ESP-IDF
here), and anything on the FPGA side.

The checks
----------
* link -> hub: frames of 14..1518 bytes, including all-zero frames and
  the COBS block boundaries (253/254/255 non-zero bytes), arrive at the
  server port byte for byte and in order.
* hub -> link: the same frames sent from the server port come out of the
  relay's link as exactly the bytes the Python encoder makes (the
  encoding is canonical), and decode back to the frames.
* bad link packets (wrong CRC, broken COBS, a runt frame, an oversized
  packet, an unknown type, line noise) are dropped and counted, and the
  good frame after each one still arrives.
* the hub's learning port (`HUB:learn`, added for the ESP32, whose
  address is DHCP's): the hub sends nothing to it until it has heard
  from it, then sends to the learned address.
* a replay of the recorded s9term session (`tests/net/a5_session.pcap`,
  1108 frames, /boot's BOOTP through `echo hello`'s output) through the
  relay paced at 2.5 Mbaud, each direction run sent as one burst (as IL
  sends a fragmented 9P message), checking every frame and that no frame
  is dropped; the time taken is printed and checked against the link
  model in docs/ulx3s_ethernet.md.

Discrimination (injected 2026-11-24 into relay.c, each reverted by the
reverse replacement, `git diff` clean after each; observed results):

1. COBS encoder: a full block closed at code 0xFE instead of 0xFF
   (`if (++e->code == 0xFE)`), so the receiver reads a spurious 0x00
   after every 253 non-zero bytes.  Observed: FAIL test_hub_to_link,
   FAIL test_session_replay; the other four pass (test_link_to_hub
   encodes in Python and decodes in C, so it does not reach the
   encoder).
2. CRC: the final inversion dropped (`return crc;`).  Observed: FAIL
   test_link_to_hub, test_hub_to_link, test_bad_packets_dropped; ERROR
   (socket timeout) test_learning_port, test_session_replay; only
   test_reference_codec passes.  (The run took 132 s, in timeouts.)
3. Decoder: the runt check removed (`if (m > RELAY_MAX_FRAME)`).
   Observed: FAIL test_bad_packets_dropped only (the 13-byte runt is
   forwarded).
"""
import json
import os
import random
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zlib

here = os.path.dirname(os.path.abspath(__file__))
hobbit = os.path.dirname(here)
sys.path.insert(0, os.path.join(hobbit, 'tools', 'qemu1e'))
from hub import Hub  # noqa: E402

RELAY = os.path.join(hobbit, 'fpga', 'esp32_ethrelay')
PCAP = os.path.join(here, 'net', 'a5_session.pcap')
T_ETH, T_STATUS = 0x45, 0x53


# --- an independent reference codec ---------------------------------------

def cobs_encode(body):
    out = bytearray()
    block = bytearray()
    for b in body:
        if b == 0:
            out.append(len(block) + 1)
            out += block
            block = bytearray()
        else:
            block.append(b)
            if len(block) == 254:
                out.append(255)
                out += block
                block = bytearray()
    out.append(len(block) + 1)
    out += block
    return bytes(out)


def cobs_decode(data):
    out = bytearray()
    i = 0
    while i < len(data):
        code = data[i]
        if code == 0 or i + code > len(data):
            raise ValueError('bad COBS')
        out += data[i + 1:i + code]
        i += code
        if code != 255 and i < len(data):
            out.append(0)
    return bytes(out)


def packet(typ, payload):
    body = bytes([typ]) + payload
    return cobs_encode(body + struct.pack('<I', zlib.crc32(body))) + b'\0'


def unpacket(enc):
    body = cobs_decode(enc)
    if len(body) < 5 or zlib.crc32(body[:-4]) != struct.unpack(
            '<I', body[-4:])[0]:
        raise ValueError('bad CRC')
    return body[0], body[1:-4]


# --- fixtures ----------------------------------------------------------------

def free_udp_ports(n):
    socks, ports = [], []
    for _ in range(n):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('127.0.0.1', 0))
        socks.append(s)
        ports.append(s.getsockname()[1])
    for s in socks:
        s.close()
    return ports


_build = {}


def relay_binary():
    if 'path' not in _build:
        d = tempfile.mkdtemp(prefix='ethrelay')
        exe = os.path.join(d, 'relay_host')
        subprocess.run(
            ['cc', '-std=c99', '-D_POSIX_C_SOURCE=200809L', '-Wall',
             '-Wextra', '-Werror', '-O2', '-o', exe,
             os.path.join(RELAY, 'host', 'relay_host.c'),
             os.path.join(RELAY, 'main', 'relay.c')], check=True)
        _build['path'] = exe
    return _build['path']


class Rig:
    """hub: port 0 the relay, port 1 the server; the server socket."""

    def __init__(self, baud=0, queue=64, learn=False):
        hub_r, relay, hub_s, srv = free_udp_ports(4)
        self.srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.srv.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1 << 20)
        self.srv.bind(('127.0.0.1', srv))
        self.srv.settimeout(5)
        rport = (hub_r, None, None, '127.0.0.1') if learn else (hub_r, relay)
        self.hub = Hub([rport, (hub_s, srv)])
        self.hub.start()
        self.hub_s = hub_s
        self.p = subprocess.Popen(
            [relay_binary(), '--hub', '127.0.0.1:%d' % hub_r,
             '--local', str(relay), '--baud', str(baud),
             '--queue', str(queue)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        self.out = []           # (type, payload) or ('bad', bytes)
        self.cv = threading.Condition()
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def _read(self):
        buf = bytearray()
        while True:
            c = self.p.stdout.read1(65536)
            if not c:
                return
            buf += c
            while b'\0' in buf:
                i = buf.index(b'\0')
                enc = bytes(buf[:i])
                del buf[:i + 1]
                try:
                    item = unpacket(enc)
                except ValueError:
                    item = ('bad', enc)
                with self.cv:
                    self.out.append(item + (enc,) if item[0] != 'bad'
                                    else item)
                    self.cv.notify_all()

    def link_write(self, data):
        self.p.stdin.write(data)
        self.p.stdin.flush()

    def server_send(self, frame):
        self.srv.sendto(frame, ('127.0.0.1', self.hub_s))

    def server_recv(self):
        return self.srv.recv(65536)

    def wait_out(self, n, timeout=10):
        end = time.time() + timeout
        with self.cv:
            while len(self.out) < n and time.time() < end:
                self.cv.wait(0.1)
            return list(self.out)

    def close(self):
        """Stops the relay; returns its counters."""
        self.p.stdin.close()
        self.p.wait(10)
        self.reader.join(5)
        err = self.p.stderr.read().decode()
        self.hub.stop()
        self.srv.close()
        return json.loads(err.strip().splitlines()[-1])


def frames():
    r = random.Random(7)
    fs = [bytes(14), bytes(60), b'\xff' * 60]
    for n in (61, 253, 254, 255, 256, 508, 509, 1000, 1514, 1518):
        fs.append(bytes(r.randrange(1, 256) for _ in range(n)))
        fs.append(bytes(r.randrange(0, 256) for _ in range(n)))
    fs.append(bytes(1518))
    return fs


def read_pcap(path):
    with open(path, 'rb') as fp:
        d = fp.read()
    o, out = 24, []
    while o < len(d):
        _, _, cl, _ = struct.unpack('<IIII', d[o:o + 16])
        out.append(d[o + 16:o + 16 + cl])
        o += 16 + cl
    return out


class EthRelayTest(unittest.TestCase):

    def test_reference_codec(self):
        """The Python codec round-trips (it is the oracle below)."""
        for f in frames():
            self.assertEqual(unpacket(packet(T_ETH, f)[:-1]), (T_ETH, f))
            self.assertNotIn(0, packet(T_ETH, f)[:-1])

    def test_link_to_hub(self):
        rig = Rig()
        try:
            got = []
            for f in frames():
                rig.link_write(packet(T_ETH, f))
                try:
                    got.append(rig.server_recv())
                except socket.timeout:
                    got.append(None)
        finally:
            st = rig.close()
        for f, g in zip(frames(), got):
            self.assertEqual(g, f, 'frame of %d bytes' % len(f))
        self.assertEqual(st['link_in'], len(frames()))

    def test_hub_to_link(self):
        rig = Rig()
        try:
            for f in frames():
                rig.server_send(f)
                time.sleep(0.002)
            out = rig.wait_out(len(frames()))
        finally:
            st = rig.close()
        self.assertEqual(len(out), len(frames()))
        for f, o in zip(frames(), out):
            self.assertNotEqual(o[0], 'bad', 'undecodable link packet')
            self.assertEqual(o[2] + b'\0', packet(T_ETH, f),
                             'link bytes of a %d-byte frame' % len(f))
            self.assertEqual(o[:2], (T_ETH, f))
        self.assertEqual(st['dropped'], 0)

    def test_bad_packets_dropped(self):
        good = [bytes([0x52, 0x54, 0, 0, 0x0b, i]) + bytes(54) for i in
                range(7)]
        p = packet(T_ETH, bytes(range(1, 61)))
        bad_crc = p[:5] + bytes([p[5] ^ 1]) + p[6:]
        bad_cobs = bytes([0x40, 1, 2, 3]) + b'\0'     # code runs off the end
        runt = packet(T_ETH, bytes(13))
        huge = b'\x01' * 2000 + b'\0'                   # > RELAY_MAX_WIRE
        unknown = packet(0x99, bytes(60))
        noise = bytes([0x13, 0x37, 0xff])
        rig = Rig()
        try:
            # Each bad packet is followed by a good frame.  The line noise
            # has no delimiter of its own, so it joins the packet after it
            # and that frame is lost (bad_crc); the next one is received.
            stream = [bad_crc, bad_cobs, runt, huge, unknown, noise, b'']
            for g, b in zip(good, stream):
                rig.link_write(b + packet(T_ETH, g))
            rig.srv.settimeout(0.5)
            got = []
            try:
                while True:
                    got.append(rig.server_recv())
            except socket.timeout:
                pass
        finally:
            st = rig.close()
        self.assertEqual(got, good[:5] + good[6:])
        self.assertEqual((st['bad_crc'], st['bad_cobs'], st['bad_len'],
                          st['overflows'], st['bad_type']),
                         (2, 1, 1, 1, 1),
                         'counters %r (the noise packet fails its CRC)' % st)

    def test_learning_port(self):
        rig = Rig(learn=True)
        try:
            first = bytes([1]) * 60
            rig.server_send(first)          # nowhere to go yet
            time.sleep(0.3)
            self.assertEqual(rig.wait_out(1, timeout=0.3), [])
            rig.link_write(packet(T_ETH, b'\xff' * 6 + bytes(54)))
            self.assertEqual(rig.server_recv(), b'\xff' * 6 + bytes(54))
            self.assertIsNotNone(rig.hub.learned[0])
            second = bytes([2]) * 60
            rig.server_send(second)
            out = rig.wait_out(1)
        finally:
            rig.close()
        self.assertEqual([o[:2] for o in out], [(T_ETH, second)])

    def test_session_replay(self):
        """s9term's recorded session through the relay at 2.5 Mbaud."""
        baud = 2500000
        fs = read_pcap(PCAP)
        hobbit_mac = fs[0][6:12]            # its BOOTP request
        runs = []
        for f in fs:
            up = f[6:12] == hobbit_mac
            if runs and runs[-1][0] == up:
                runs[-1][1].append(f)
            else:
                runs.append((up, [f]))
        rig = Rig(baud=baud, queue=16)
        t0 = time.time()
        sent_down = 0
        try:
            for up, burst in runs:
                if up:
                    rig.link_write(b''.join(packet(T_ETH, f) for f in burst))
                    for f in burst:
                        self.assertEqual(rig.server_recv(), f)
                else:
                    for f in burst:
                        rig.server_send(f)
                    sent_down += len(burst)
                    out = rig.wait_out(sent_down)
                    self.assertEqual(len(out), sent_down)
            took = time.time() - t0
        finally:
            st = rig.close()
        down = [f for f in fs if f[6:12] != hobbit_mac]
        up = [f for f in fs if f[6:12] == hobbit_mac]
        self.assertEqual([o[1] for o in rig.out], down)
        self.assertEqual(st['dropped'], 0)
        self.assertEqual(st['link_in'], len(up))
        wire = sum(len(packet(T_ETH, f)) for f in fs)
        model = wire * 10 / baud
        print('\nsession replay: %d frames (%d up, %d down), %d link bytes; '
              '%.2f s at %d baud, link model %.2f s; max queue %d'
              % (len(fs), len(up), len(down), wire, took, baud, model,
                 st['max_queue']))
        # the link time is a floor; the rest is the run-by-run turnaround
        self.assertGreater(took, model * 0.95)
        self.assertLess(took, model + 0.02 * len(runs) + 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
