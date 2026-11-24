#!/usr/bin/env python3
"""End-to-end test of the terminal boot path over IL: two QEMUs.

  server    9dos.q from fd.img, kfs on fs.img, `rc /serve 10.9.0.1 ...`
  terminal  9pc.qs (the shipped 9pc, a terminal kernel) from fd-term.img,
            no disk; its /boot answers `root is from` with `il`

joined by a QEMU `dgram` netdev pair: each NE2000's frames are UDP
datagrams between 127.0.0.1:PORT_S and 127.0.0.1:PORT_T, one Ethernet
frame per datagram, no other framing -- the boundary the Hobbit model's
SONIC is to be attached at instead of the terminal QEMU.

The terminal's /boot does BOOTP (answered by the server's ip/bootp from
ndb.local), ARP, dials il!10.9.0.1!17008, sends Tnop/Tsession, mounts
the root as user none (so no auth server is consulted:
boot/userpasswd.c), and execs /386/init from the server.  The test
passes when the terminal's rc lists /hobbit from the server.

Run from anywhere after build.sh; writes logs and server.pcap under
build/qemu/run-il/.
"""
import os
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import qemu1e  # noqa: E402

Q = os.path.normpath(os.path.join(here, '..', '..', 'build', 'qemu'))
PS, PT = int(os.environ.get('PORT_S', 10901)), int(os.environ.get('PORT_T', 10902))


def dgram(local, remote):
    return ('-netdev dgram,id=n0,local.type=inet,local.host=127.0.0.1,local.port=%d,'
            'remote.type=inet,remote.host=127.0.0.1,remote.port=%d' % (local, remote))


def login(m, root):
    m.wait('boot from', 30)
    m.type('\n')
    m.wait('root is from', 60)
    m.type(root + '\n')


def main():
    wd = os.path.join(Q, 'run-il')
    os.makedirs(wd, exist_ok=True)
    nic = '-device ne2k_isa,iobase=0x300,irq=9,netdev=n0'
    srv = qemu1e.Machine(
        wd, fd=os.path.join(Q, 'fd.img'), hd=os.path.join(Q, 'fs.img'),
        hd2=os.path.join(Q, 'arch.img'),
        net=(dgram(PS, PT) + ' ' + nic + ',mac=52:54:00:12:34:56'
             + ' -object filter-dump,id=f0,netdev=n0,file=server.pcap').split(),
        log=os.path.join(wd, 'server.log'))
    term = None
    try:
        login(srv, '')
        srv.wait('user', 60)
        srv.type('glenda\n')
        srv.wait('password', 10)
        srv.type('password\n')
        srv.wait('^%', 60)
        srv.type('rc /serve 10.9.0.1 255.255.255.0\n')
        s = srv.wait('tcp: announced', 120)   # 'serving' can be split by syslog lines
        srv._log(s)
        print('--- server\n' + s.rstrip())

        term = qemu1e.Machine(
            wd, fd=os.path.join(Q, 'fd-term.img'),
            net=(dgram(PT, PS) + ' ' + nic + ',mac=52:54:00:12:34:57').split(),
            # the release's termrc runs `aux/mouse 1` on a generic PC
            # (a serial mouse on COM2): give it one
            extra=['-serial', 'msmouse'],
            log=os.path.join(wd, 'term.log'))
        login(term, 'il')
        s = term.wait(r'user\[none\]:|My IP address', 120)
        term._log(s)
        if 'My IP address' in s:
            raise SystemExit('no BOOTP reply:\n' + s)
        term.type('\n')
        s = term.wait('init: starting', 300)
        term._log(s)
        try:
            s = term.wait('^% *$', 60)
        except TimeoutError:
            # the release's termrc (case generic*) stops after ip/ipconfig;
            # DEL interrupts it and init goes on to rc
            term.type('\x7f')
            s = term.wait('^% *$', 60)
        term._log(s)
        print('--- terminal booted\n' + s.rstrip())
        term.type('cat /dev/user; echo; ls -l /hobbit; ls /rc/bin/service.9fs\n')
        time.sleep(8)
        s = term.screen()
        term._log(s)
        print('--- terminal\n' + s.rstrip())
        s2 = srv.screen()
        srv._log(s2)
        print('--- server\n' + s2.rstrip())
        ok = 's9term' in s and 'il17008' in s
        print('PASS' if ok else 'FAIL')
        sys.exit(0 if ok else 1)
    finally:
        for m in (term, srv):
            if m:
                m.quit()


if __name__ == '__main__':
    main()
