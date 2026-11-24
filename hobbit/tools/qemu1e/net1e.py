"""The 1e network in QEMU: names, addresses, passwords, and the steps
the scripts share (docs/qemu_1e_server.md section 5).

  fs9      10.9.0.1  525400123456  9dos.q, floppy root, kfs: file server
                                   (il 17008, tcp 564), BOOTP, and the
                                   authentication server (keyfs, il
                                   17020-17024)
  hobbit   10.9.0.2  525400000b0b  s9term on the Bluespec model
  term386  10.9.0.3  525400123457  the shipped 9pc: a terminal
  cpu9     10.9.0.4  525400123458  9pccpu, built in the guest: the CPU
                                   server (il 17005)

Passwords.  These are a test network's, and are written down here on
purpose: the scripts type them.
  FS9_PW     typed at fs9's boot; with no nvram, its key is the one
             keyfs -d decrypts /adm/keys with (serve.rc), so it must be
             the same at every boot (the old scripts already typed it)
  GLENDA_PW  glenda's password, in /adm/keys (authinit.rc)
  CPU9_PW    cpu9's host key: in /adm/keys as the host cpu9, and typed
             at cpu9's boot (boot/key.c asks for it when there is no
             #r/nvram)
"""
import os
import re
import time

FS9_PW = 'password'
GLENDA_PW = 'glenda93'
CPU9_PW = 'cpu9host'

MAC = {'fs9': '52:54:00:12:34:56', 'term386': '52:54:00:12:34:57',
       'cpu9': '52:54:00:12:34:58'}
NIC = '-device ne2k_isa,iobase=0x300,irq=9,netdev=n0'


def dgram(local, remote):
    return ('-netdev dgram,id=n0,local.type=inet,local.host=127.0.0.1,'
            'local.port=%d,remote.type=inet,remote.host=127.0.0.1,'
            'remote.port=%d' % (local, remote))


def net(name, local, remote, pcap=None):
    a = dgram(local, remote) + ' ' + NIC + ',mac=' + MAC[name]
    if pcap:
        a += ' -object filter-dump,id=f0,netdev=n0,file=' + pcap
    return a.split()


def last_line(s):
    lines = [l for l in s.split('\n') if l.strip()]
    return lines[-1] if lines else ''


def wait_prompt(m, pat, timeout=60):
    """Wait until the last non-blank screen line matches pat: a prompt
    at the cursor, not an old one further up the screen."""
    rx = re.compile(pat)
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = m.screen()
        if rx.search(last_line(s)):
            m.last = s
            return s
        if m.p.poll() is not None:
            break
        time.sleep(0.5)
    raise TimeoutError('no prompt /%s/ after %ds; screen:\n%s'
                       % (pat, timeout, m.screen()))


def boot(m, root='', user=None, password=None):
    """b.com's prompt (default fd!0!9dos), then /boot's `root is from`."""
    m.wait('boot from', 60)
    m.type('\n')
    m.wait('root is from', 120)
    m.type(root + '\n')
    if user is not None:
        m.wait('user', 120)
        m.type(user + '\n')
        m.wait('password', 30)
        m.type(password + '\n')


def boot_fs9(m):
    """The floppy system as glenda, to rc's prompt."""
    boot(m, '', 'glenda', FS9_PW)
    m.wait('^%', 120)


def serve(m, ip='10.9.0.1', mask='255.255.255.0'):
    m.type('rc /serve %s %s\n' % (ip, mask))
    # 'serving', even 'announced', can be split by the prompt or syslog lines
    return m.wait('tcp: announce', 180)


def screen_log(m, tag, out=print):
    s = m.screen()
    m._log(s)
    out('--- %s\n%s' % (tag, s.rstrip()))
    return s


def path(*a):
    """build/<a...>; build/qemu itself can be redirected with $QEMU1E_Q
    (a directory holding fd.img, fs.img, arch.img, fd-term.img: a copy to
    experiment on, as overlay.sh also honours)."""
    if a and a[0] == 'qemu' and os.environ.get('QEMU1E_Q'):
        return os.path.join(os.path.abspath(os.environ['QEMU1E_Q']), *a[1:])
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, '..', '..', 'build', *a))
