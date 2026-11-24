#!/usr/bin/env python3
"""Drive a 1st Edition Plan 9 PC (9pc/9dos) in qemu-system-i386.

The 1e PC kernels have no serial console: console output goes to
`screenputs` (sys/src/9/pc/devvga.c:812, cga.c:51) and input comes from
the keyboard (kbd.c); devuart.c's `uartspecial` "console interface" has
one caller, the serial mouse (kbd.c:278).  So this driver
runs QEMU headless and

  * reads the screen by dumping the CGA text buffer (physical 0xB8000,
    80x25 cells of char+attribute) with QMP `pmemsave`, and
  * types by QMP `send-key`, one key event per character.

Used as a library (`Machine`) by the other scripts here, or from the
command line:

    qemu1e.py [--fd IMG] [--hd IMG] [--net ARGS] [--log FILE] SCRIPT

where SCRIPT is a file of lines:

    wait <regex> [timeout]   wait until the screen matches
    type <text>              type text; \\n is Return
    sleep <seconds>
    screen                   print the screen
    host <shell command>     run a host command (fails the script on error)
    quit

Every QEMU process this starts is killed by PID on exit.
"""
import json
import os
import re
import socket
import subprocess
import sys
import time

QEMU = os.environ.get('QEMU', '/opt/homebrew/bin/qemu-system-i386')

# US keyboard: character -> (qcode, shift)
KEYS = {' ': ('spc', 0), '\n': ('ret', 0), '\t': ('tab', 0),
        '\b': ('backspace', 0), '\x1b': ('esc', 0), '\x7f': ('delete', 0)}
for c in 'abcdefghijklmnopqrstuvwxyz':
    KEYS[c] = (c, 0)
    KEYS[c.upper()] = (c, 1)
for c in '0123456789':
    KEYS[c] = (c, 0)
for c, k in zip(')!@#$%^&*(', '0123456789'):
    KEYS[c] = (k, 1)
for c, k, s in [('-', 'minus', 0), ('_', 'minus', 1), ('=', 'equal', 0),
                ('+', 'equal', 1), ('[', 'bracket_left', 0),
                ('{', 'bracket_left', 1), (']', 'bracket_right', 0),
                ('}', 'bracket_right', 1), (';', 'semicolon', 0),
                (':', 'semicolon', 1), ("'", 'apostrophe', 0),
                ('"', 'apostrophe', 1), ('`', 'grave_accent', 0),
                ('~', 'grave_accent', 1), ('\\', 'backslash', 0),
                ('|', 'backslash', 1), (',', 'comma', 0), ('<', 'comma', 1),
                ('.', 'dot', 0), ('>', 'dot', 1), ('/', 'slash', 0),
                ('?', 'slash', 1)]:
    KEYS[c] = (k, s)


class Machine:
    n = 0

    def __init__(self, workdir, fd=None, hd=None, hd2=None, net=None,
                 mem=16, serial=None, extra=(), log=None, boot='a'):
        self.workdir = workdir
        os.makedirs(workdir, exist_ok=True)
        Machine.n += 1
        self.id = '%d.%d' % (os.getpid(), Machine.n)    # one QMP socket per QEMU
        self.sock = 'qmp.%s.sock' % self.id
        args = [QEMU, '-M', 'isapc', '-cpu', '486', '-m', str(mem),
                '-display', 'none', '-vga', 'std',
                '-qmp', 'unix:%s,server=on,wait=off' % self.sock,
                '-boot', boot, '-no-reboot', '-rtc', 'base=1993-01-03T12:00:00']
        if fd:
            args += ['-drive', 'file=%s,if=floppy,format=raw,index=0'
                     % os.path.abspath(fd)]
        if hd:
            args += ['-drive', 'file=%s,if=ide,format=raw,index=0'
                     % os.path.abspath(hd)]
        if hd2:
            args += ['-drive', 'file=%s,if=ide,format=raw,index=1'
                     % os.path.abspath(hd2)]
        if net:
            args += net
        else:
            args += ['-nic', 'none']
        args += ['-serial', serial or 'null']
        args += list(extra)
        self.args = args
        self.log = open(log, 'a') if log else None
        self._log('# ' + ' '.join(args))
        self.p = subprocess.Popen(args, cwd=workdir,
                                  stdout=subprocess.DEVNULL,
                                  stderr=open(os.path.join(workdir, 'qemu.%s.stderr' % self.id), 'w'))
        path = os.path.join(workdir, self.sock)
        for _ in range(100):
            if os.path.exists(path):
                break
            if self.p.poll() is not None:
                raise RuntimeError('qemu exited: ' + open(os.path.join(
                    workdir, 'qemu.%s.stderr' % self.id)).read())
            time.sleep(0.1)
        cwd = os.getcwd()
        os.chdir(workdir)
        try:
            self.s = socket.socket(socket.AF_UNIX)
            self.s.connect(self.sock)
        finally:
            os.chdir(cwd)
        self.f = self.s.makefile('rw')
        json.loads(self.f.readline())
        self.cmd('qmp_capabilities')
        self.last = ''

    def _log(self, s):
        if self.log:
            self.log.write(s + '\n')
            self.log.flush()

    def cmd(self, name, **args):
        self.f.write(json.dumps({'execute': name, 'arguments': args}) + '\n')
        self.f.flush()
        while True:
            r = json.loads(self.f.readline())
            if 'return' in r or 'error' in r:
                if 'error' in r:
                    raise RuntimeError(r['error'])
                return r['return']

    def screen(self):
        fn = os.path.join(self.workdir, 'cga.%s.bin' % self.id)
        self.cmd('pmemsave', val=0xB8000, size=4000, filename=os.path.abspath(fn))
        b = open(fn, 'rb').read()
        rows = []
        for r in range(25):
            row = b[r * 160:(r + 1) * 160:2]
            rows.append(row.replace(b'\0', b' ').decode('latin-1').rstrip())
        return '\n'.join(rows)

    def wait(self, pat, timeout=60):
        rx = re.compile(pat, re.M)
        t0 = time.time()
        while time.time() - t0 < timeout:
            s = self.screen()
            if rx.search(s):
                self.last = s
                return s
            if self.p.poll() is not None:
                break
            time.sleep(0.5)
        self.last = self.screen() if self.p.poll() is None else self.last
        raise TimeoutError('no /%s/ after %ds; screen:\n%s' % (pat, timeout, self.last))

    def type(self, text, delay=0.03):
        self._log('> ' + repr(text))
        for c in text:
            k, sh = KEYS[c]
            keys = [{'type': 'qcode', 'data': 'shift'}] if sh else []
            keys.append({'type': 'qcode', 'data': k})
            self.cmd('send-key', keys=keys, **{'hold-time': 20})
            time.sleep(delay)

    def quit(self):
        try:
            self.cmd('quit')
        except Exception:
            pass
        try:
            self.p.wait(5)
        except subprocess.TimeoutExpired:
            self.p.kill()
        for fn in (self.sock, 'cga.%s.bin' % self.id):
            try:
                os.unlink(os.path.join(self.workdir, fn))
            except OSError:
                pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        if self.p.poll() is None:
            self.p.kill()
            self.p.wait()


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--fd')
    ap.add_argument('--hd')
    ap.add_argument('--hd2')
    ap.add_argument('--net', action='append', default=[])
    ap.add_argument('--serial')
    ap.add_argument('--workdir', default='.')
    ap.add_argument('--log')
    ap.add_argument('--extra', action='append', default=[])
    ap.add_argument('script')
    a = ap.parse_args()
    net = []
    for n in a.net:
        net += n.split()
    m = Machine(a.workdir, fd=a.fd, hd=a.hd, hd2=a.hd2, net=net or None, serial=a.serial,
                log=a.log, extra=sum([e.split() for e in a.extra], []))
    try:
        for line in open(a.script):
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            op, _, arg = line.partition(' ')
            if op == 'wait':
                pat, _, to = arg.rpartition(' ')
                if not to.isdigit():
                    pat, to = arg, '60'
                s = m.wait(pat, int(to))
                m._log(s)
            elif op == 'type':
                m.type(arg.encode().decode('unicode_escape'))
            elif op == 'host':
                m._log('$ ' + arg)
                r = subprocess.run(arg, shell=True, capture_output=True, text=True)
                print(r.stdout + r.stderr, end='')
                m._log(r.stdout + r.stderr)
                if r.returncode:
                    raise RuntimeError('host command failed: ' + arg)
            elif op == 'sleep':
                time.sleep(float(arg))
            elif op == 'screen':
                s = m.screen()
                print(s)
                m._log(s)
            elif op == 'quit':
                break
    finally:
        m.quit()
        m.__exit__()


if __name__ == '__main__':
    main()
