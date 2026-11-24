#!/usr/bin/env python3
"""An Ethernet hub for QEMU `dgram` netdevs (and the Hobbit model's SONIC).

A `-netdev dgram` joins exactly two ends: one Ethernet frame per UDP
datagram between a local and a remote port (docs/qemu_1e_server.md, "The
netdev").  The 1e network here has more than two machines (the file and
auth server fs9, the CPU server cpu9, a terminal), so each machine's
netdev is pointed at a port of this hub instead, and the hub repeats
every frame it receives on one port out of all the others, as a 10BASE2
segment would.  No learning, no filtering: the traffic is a few
thousand frames.

Each port is a pair (hub, peer): the hub receives on 127.0.0.1:hub and
sends to 127.0.0.1:peer.  So a machine started with
`local.port=P,remote.port=H` is attached by the port (H, P).  The file
server keeps its usual pair (local 10901, remote 10902), so the hub's
port for it is (10902, 10901): exactly where the terminal end of the
two-machine set-up sat (il_term_test.py, p9join.py).

    hub.py HUB:PEER [HUB:PEER ...]      (runs until killed)

or as a library: Hub([(h, p), ...]).start(), .stop(); .counts[i] is the
number of frames received on port i.

Ports off this host (2026-11-24, docs/ulx3s_ethernet.md): the ULX3S's
ESP32 relays the board's frames over WiFi, so its port must be reachable
from the LAN and its peer is not 127.0.0.1.  Two more spellings, same
framing (one raw frame per datagram):

    HUB:HOST:PEER   bind 0.0.0.0:HUB, send to HOST:PEER
    HUB:learn       bind 0.0.0.0:HUB, send to the source address of the
                    last datagram received on it (nothing is sent to the
                    port until its first datagram arrives)

As a library, a port is (h, p) as before, or (h, p, peer_host, bind_host)
with p None for a learning port.  .learned[i] is port i's learned peer.

A port may be given a destination filter (`filters={i: [mac, ...]}`, six
bytes each): then only frames addressed to one of those stations, or to
broadcast or multicast (the group bit), are repeated out of it, as a
switch port would; the others are counted in .filtered[i].  p9join.py
filters the Hobbit's port to its own address: the model's SONIC drops
the other frames itself (its CAM, docs/p9boot.md SONIC_CHOICES
['filter']), so the filter changes nothing the Hobbit sees, but it keeps
the fs9-cpu9 traffic (cpu9's root is on fs9) out of the Hobbit's
lockstep wait and out of its recording.  `pcap=PATH` writes every frame
the hub receives, stamped with the host's clock (microseconds), as an
artifact of the whole segment.
"""
import select
import socket
import struct
import sys
import threading
import time


class Hub(threading.Thread):
    def __init__(self, ports, host='127.0.0.1', log=None, filters=None,
                 pcap=None):
        super().__init__(daemon=True)
        self.filters = {i: set(bytes(m) for m in macs)
                        for i, macs in (filters or {}).items()}
        self.filtered = [0] * len(ports)
        self.pcap = None
        if pcap:
            self.pcap = open(pcap, 'wb')
            self.pcap.write(struct.pack('<IHHiIII', 0xA1B2C3D4, 2, 4, 0, 0,
                                        65535, 1))
        self.socks = []
        self.peers = []
        self.learn = []
        for port in ports:
            h, p = port[0], port[1]
            peer_host = port[2] if len(port) > 2 else host
            bind_host = port[3] if len(port) > 3 else host
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind((bind_host, h))
            self.socks.append(s)
            self.learn.append(p is None)
            self.peers.append(None if p is None else (peer_host, p))
        self.learned = [None] * len(ports)
        self.counts = [0] * len(ports)
        self.log = log
        self.running = True

    def run(self):
        while self.running:
            r, _, _ = select.select(self.socks, [], [], 0.2)
            for s in r:
                i = self.socks.index(s)
                frame, src = s.recvfrom(65536)
                self.counts[i] += 1
                if self.learn[i]:
                    self.peers[i] = self.learned[i] = src
                if self.pcap:
                    us = int(time.time() * 1e6)
                    self.pcap.write(struct.pack('<IIII', us // 1000000,
                                                us % 1000000, len(frame),
                                                len(frame)) + frame)
                for j, t in enumerate(self.socks):
                    if j == i or self.peers[j] is None:
                        continue
                    f = self.filters.get(j)
                    if (f is not None and not frame[0] & 1
                            and frame[:6] not in f):
                        self.filtered[j] += 1
                        continue
                    t.sendto(frame, self.peers[j])

    def stop(self):
        self.running = False
        self.join(2)
        for s in self.socks:
            s.close()
        if self.pcap:
            self.pcap.close()


def parse_port(a):
    """One command-line port: HUB:PEER, HUB:HOST:PEER or HUB:learn."""
    f = a.split(':')
    if len(f) == 2 and f[1] == 'learn':
        return (int(f[0]), None, None, '0.0.0.0')
    if len(f) == 2:
        return (int(f[0]), int(f[1]))
    if len(f) == 3:
        return (int(f[0]), int(f[2]), f[1], '0.0.0.0')
    raise ValueError('bad port %r' % a)


def main():
    try:
        ports = [parse_port(a) for a in sys.argv[1:]]
    except ValueError as e:
        sys.exit(str(e))
    if len(ports) < 2:
        sys.exit('usage: hub.py HUB:PEER|HUB:HOST:PEER|HUB:learn ...')
    hub = Hub(ports)
    hub.start()
    try:
        hub.join()
    except KeyboardInterrupt:
        hub.stop()


if __name__ == '__main__':
    main()
