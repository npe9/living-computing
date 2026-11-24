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
"""
import select
import socket
import sys
import threading


class Hub(threading.Thread):
    def __init__(self, ports, host='127.0.0.1', log=None):
        super().__init__(daemon=True)
        self.socks = []
        self.peers = []
        for h, p in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind((host, h))
            self.socks.append(s)
            self.peers.append((host, p))
        self.counts = [0] * len(ports)
        self.log = log
        self.running = True

    def run(self):
        while self.running:
            r, _, _ = select.select(self.socks, [], [], 0.2)
            for s in r:
                i = self.socks.index(s)
                frame, _ = s.recvfrom(65536)
                self.counts[i] += 1
                for j, t in enumerate(self.socks):
                    if j != i:
                        t.sendto(frame, self.peers[j])

    def stop(self):
        self.running = False
        self.join(2)
        for s in self.socks:
            s.close()


def main():
    ports = []
    for a in sys.argv[1:]:
        h, _, p = a.partition(':')
        ports.append((int(h), int(p)))
    if len(ports) < 2:
        sys.exit('usage: hub.py HUB:PEER HUB:PEER [...]')
    hub = Hub(ports)
    hub.start()
    try:
        hub.join()
    except KeyboardInterrupt:
        hub.stop()


if __name__ == '__main__':
    main()
