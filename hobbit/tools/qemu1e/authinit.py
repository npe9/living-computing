#!/usr/bin/env python3
"""Make the authentication database in build/qemu/fs.img (written, not a
snapshot): boot the floppy system and run /authinit (authinit.rc), typing
the passwords of net1e.py at auth/adduser's prompts
(sys/src/auth/readln.c: `Password: `, `Confirm password: `).

Run after build.sh (or on an fs.img that has the overlay); once is
enough: a second run fails at `user glenda already exists`
(adduser.c check) and changes nothing.  Writes
build/qemu/run-auth/authinit.log.
"""
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import qemu1e  # noqa: E402
import net1e   # noqa: E402

Q = net1e.path('qemu')


def adduser(m, pw):
    net1e.wait_prompt(m, r'^Password: *$', 120)
    m.type(pw + '\n')
    net1e.wait_prompt(m, r'^Confirm password: *$', 30)
    m.type(pw + '\n')


def main():
    wd = os.path.join(Q, 'run-auth')
    m = qemu1e.Machine(wd, fd=os.path.join(Q, 'fd.img'),
                       hd=os.path.join(Q, 'fs.img'),
                       hd2=os.path.join(Q, 'arch.img'),
                       log=os.path.join(wd, 'authinit.log'))
    try:
        net1e.boot_fs9(m)
        m.type('rc /authinit\n')
        adduser(m, net1e.GLENDA_PW)
        m.wait('user glenda installed', 60)
        adduser(m, net1e.CPU9_PW)
        s = m.wait('^authinit done', 120)
        m._log(s)
        print(s.rstrip())
        ok = 'user cpu9 installed' in s or 'cpu9' in s
        print('PASS' if ok else 'FAIL')
        sys.exit(0 if ok else 1)
    finally:
        m.quit()


if __name__ == '__main__':
    main()
