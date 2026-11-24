#!/usr/bin/env python3
"""The 1e network end to end: file and auth server, CPU server, terminal.

  fs9      9dos.q from fd.img, kfs on fs.img (-snapshot): `rc /serve`,
           which is also the authentication server (keyfs, il 17020-24)
  cpu9     9pccpu.qs from build/qemu-cpu/fd-cpu.img (cpukernel.sh), no
           disk: /boot asks `root is from` (il) and, with no #r/nvram,
           the host key's password (boot/key.c); its root is fs9's kfs
           over IL; after cpurc, init asks the host key again to unlock
           the console (init.c pass); there `ip/ipconfig; aux/listen il`
           as cpurc's kremvax case does (il17005 = `cpu -R`)
  term386  the shipped 9pc from fd-term.img: a terminal

joined by hub.py (three dgram netdevs; fs9 keeps the 10901/10902 pair
shifted by PORT_BASE).

Steps, each checked on a screen:
  1. login: the terminal boots as glenda.  First a wrong password:
     /boot must say nothing of `password not checked!` and ask `user`
     again (boot/userpasswd.c: check answered NO); then GLENDA_PW: init
     starts, /dev/user is glenda.  fs9's console logs check's `user
     glenda ok`.
  2. cpu (skipped with --login-only, or if fd-cpu.img is missing): at
     the terminal's rc, `cpu -h cpu9`; at the remote prompt, commands
     whose answers can only come from cpu9: /dev/sysname is cpu9 (the
     terminal's is term386), /dev/user glenda, and the terminal's name
     space is at /mnt/term.

    net_test.py [--login-only]
Env: PORT_BASE (default 10901; the hub uses PORT_BASE..+5).
Writes build/qemu-cpu/run-net/{fs9,cpu9,term}.log and fs9.pcap.
"""
import os
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import qemu1e  # noqa: E402
import net1e   # noqa: E402
from hub import Hub  # noqa: E402

Q = net1e.path('qemu')
C = net1e.path('qemu-cpu')
B = int(os.environ.get('PORT_BASE', 10901))


def main():
    login_only = '--login-only' in sys.argv
    fdcpu = os.path.join(C, 'fd-cpu.img')
    if not login_only and not os.path.exists(fdcpu):
        print('no %s (cpukernel.sh): login only' % fdcpu)
        login_only = True
    wd = os.path.join(C, 'run-net')
    os.makedirs(wd, exist_ok=True)
    ports = [(B + 1, B), (B + 3, B + 2)]
    if not login_only:
        ports.append((B + 5, B + 4))
    hub = Hub(ports)
    hub.start()
    fs9 = cpu9 = term = None
    ok = True
    try:
        fs9 = qemu1e.Machine(
            wd, fd=os.path.join(Q, 'fd.img'), hd=os.path.join(Q, 'fs.img'),
            hd2=os.path.join(Q, 'arch.img'),
            net=net1e.net('fs9', B, B + 1, pcap='fs9.pcap'),
            extra=['-snapshot'], log=os.path.join(wd, 'fs9.log'))
        net1e.boot_fs9(fs9)
        net1e.serve(fs9)
        net1e.screen_log(fs9, 'fs9 serving')

        if not login_only:
            cpu9 = qemu1e.Machine(
                wd, fd=fdcpu, net=net1e.net('cpu9', B + 4, B + 5),
                extra=['-snapshot'], log=os.path.join(wd, 'cpu9.log'))
            net1e.boot(cpu9, 'il')
            # boot/key.c: no #r/nvram on a PC, so it asks
            cpu9.wait('password', 120)
            cpu9.type(net1e.CPU9_PW + '\n')
            # after cpurc, init locks a CPU server's console with the
            # host key (init.c pass(): reads #c/key, which only a
            # cpuserver kernel lets eve read, port/devcons.c Qkey)
            net1e.wait_prompt(cpu9, r'cpu9 password: *$', 600)
            cpu9.type(net1e.CPU9_PW + '\n')
            s = net1e.wait_prompt(cpu9, r'% *$', 120)
            net1e.screen_log(cpu9, 'cpu9 booted')
            # what cpurc's kremvax case does: ip/ipconfig (it execs
            # ip/arpd, ipconfig.c; /boot's ARP answerer dies with /boot,
            # boot/ip.c, so without it nobody can reach cpu9), then
            # aux/listen il with the release's /bin/service (il17005 cpu -R)
            cpu9.type('ip/ipconfig; aux/listen il; cat /dev/sysname; echo; cat /dev/user; echo\n')
            time.sleep(5)
            net1e.screen_log(cpu9, 'cpu9 listening')

        term = qemu1e.Machine(
            wd, fd=os.path.join(Q, 'fd-term.img'),
            net=net1e.net('term386', B + 2, B + 3),
            # termrc runs `aux/mouse 1` on a generic PC: give it a mouse
            extra=['-serial', 'msmouse'], log=os.path.join(wd, 'term.log'))
        net1e.boot(term, 'il')
        term.wait(r'user\[none\]:', 180)
        # 1. a wrong password: check says NO, /boot asks user again
        term.type('glenda\n')
        term.wait('password', 30)
        term.type('wrongpw1\n')
        s = net1e.wait_prompt(term, r'^user\[glenda\]: *$', 120)
        s = net1e.screen_log(term, 'terminal after a wrong password')
        if 'not checked' in s:
            print('FAIL: password not checked')
            ok = False
        # ... then the right one
        term.type('\n')
        term.wait('password', 30)
        t0 = time.time()
        term.type(net1e.GLENDA_PW + '\n')
        s = term.wait('init: starting', 300)
        print('--- user glenda: password to init in %.0fs' % (time.time() - t0))
        try:
            s = net1e.wait_prompt(term, r'^% *$', 120)
        except TimeoutError:
            term.type('\x7f')      # termrc stuck after ipconfig: DEL
            s = net1e.wait_prompt(term, r'^% *$', 60)
        term.type('cat /dev/user; echo; cat /dev/sysname; echo\n')
        time.sleep(5)
        s = net1e.screen_log(term, 'terminal logged in')
        if 'not checked' in s or '\nglenda\n' not in s + '\n':
            print('FAIL: login')
            ok = False
        s = net1e.screen_log(fs9, 'fs9 after the login')
        if 'user glenda ok' not in s:
            print('FAIL: no `user glenda ok` from check on fs9')
            ok = False

        if not login_only:
            term.type('cpu -h cpu9\n')
            net1e.wait_prompt(term, r'% *$', 300)
            time.sleep(3)
            net1e.screen_log(term, 'cpu connected?')
            term.type('ls /mnt/term/hobbit; cat /dev/sysname; echo; cat /dev/user; echo; echo end of cpu\n')
            term.wait('^end of cpu', 120)
            time.sleep(3)
            s = net1e.screen_log(term, 'terminal running cpu')
            if '\ncpu9\nglenda\n' not in s or '/mnt/term/hobbit/s9term' not in s:
                print('FAIL: remote /dev/sysname, /dev/user or /mnt/term')
                ok = False
            net1e.screen_log(cpu9, 'cpu9 after cpu')
            net1e.screen_log(fs9, 'fs9 after cpu')
        print('hub frames per port:', hub.counts)
        print('PASS' if ok else 'FAIL')
        sys.exit(0 if ok else 1)
    finally:
        for m in (term, cpu9, fs9):
            if m:
                m.quit()
        hub.stop()


if __name__ == '__main__':
    main()
