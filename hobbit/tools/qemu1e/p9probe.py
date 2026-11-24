#!/usr/bin/env python3
"""Host-side probe that speaks 1st Edition 9P to the QEMU 1e file server.

The messages are the 1e ones (sys/include/fcall.h:45-83; layouts from
sys/src/libc/9sys/convS2M.c): little-endian, fixed-width NUL-padded
strings, NAMELEN 28, DIRLEN 116, a 3-byte header type[1] tag[2], and no
length prefix.  On TCP the server's end has the `fcall` line discipline
pushed (exportfs -c), and a 1e reader needs each message whole
(convM2S.c:185-187), so each T-message is sent with one write and the
replies are split here by their known sizes.

The probe replays what a terminal's boot does on its root connection
(sys/src/9/boot/boot.c:95-113, nopsession.c): Tnop and Tsession with tag
NOTAG, then the kernel mount driver's Tattach (devmnt.c mattach: uname
= the user, aname "", auth all zero) -- and then reads a directory and a
file and compares the file with the host's copy of the release.

With --walk LIST (mkarchive.py --list), it then walks the whole served
tree -- Tclone/Twalk/Topen/Tread of every directory -- and compares
every path and length with LIST; paths the server has beyond LIST are
counted under the service's bind points (/bin, /dev, /net) and listed
elsewhere (files the server itself wrote, e.g. /adm/mkext.log).

usage: p9probe.py HOST PORT TREE|TARBALL [--walk LIST] [path ...]
"""
import os
import socket
import struct
import sys
import tarfile

NAMELEN, DIRLEN, ERRLEN = 28, 116, 64
NOTAG = 0xFFFF
(Tnop, Rnop, Tsession, Rsession, Terror, Rerror, Tflush, Rflush, Tattach,
 Rattach, Tclone, Rclone, Twalk, Rwalk, Topen, Ropen, Tcreate, Rcreate, Tread,
 Rread, Twrite, Rwrite, Tclunk, Rclunk, Tremove, Rremove, Tstat, Rstat) = range(50, 78)
CHDIR = 0x80000000

# fixed sizes of R-messages; Rread is 8+count
RSIZE = {Rnop: 3, Rsession: 3, Rerror: 67, Rflush: 3, Rattach: 13, Rclone: 5,
         Rwalk: 13, Ropen: 13, Rcreate: 13, Rwrite: 7, Rclunk: 5,
         Rremove: 5, Rstat: 121}


def s(x, n):
    b = x.encode()
    assert len(b) < n
    return b + bytes(n - len(b))


class Conn:
    def __init__(self, host, port):
        self.sock = socket.create_connection((host, port), timeout=30)
        self.buf = b''
        self.tag = 0

    def recvn(self, n):
        while len(self.buf) < n:
            d = self.sock.recv(65536)
            if not d:
                raise EOFError('connection closed with %r pending' % self.buf)
            self.buf += d
        r, self.buf = self.buf[:n], self.buf[n:]
        return r

    def rpc(self, typ, body=b'', tag=None):
        if tag is None:
            self.tag += 1
            tag = self.tag
        msg = struct.pack('<BH', typ, tag) + body
        self.sock.sendall(msg)
        hdr = self.recvn(3)
        rtyp, rtag = struct.unpack('<BH', hdr)
        if rtyp == Rread:
            rest = self.recvn(5)
            fid, count, pad = struct.unpack('<HHB', rest)
            data = self.recvn(count)
            rep = rest + data
        else:
            if rtyp not in RSIZE:
                # not 9P: most likely the service's stderr (listen dups
                # the connection onto fds 0-2), so show it
                self.sock.settimeout(3)
                try:
                    more = self.sock.recv(4096)
                except OSError:
                    more = b''
                raise ValueError('reply is not 9P: %r' % (hdr + self.buf + more))
            rep = self.recvn(RSIZE[rtyp] - 3)
        if rtag != tag:
            raise ValueError('tag %d for %d' % (rtag, tag))
        if rtyp == Rerror:
            raise IOError('Rerror: ' + rep.split(b'\0')[0].decode())
        if rtyp != typ + 1:
            raise ValueError('reply %d to %d' % (rtyp, typ))
        return msg, hdr + rep

    def qid(self, rep):
        fid, path, vers = struct.unpack('<HII', rep[3:13])
        return path, vers


def dirent(b):
    name, uid, gid = (b[i:i + 28].split(b'\0')[0].decode() for i in (0, 28, 56))
    path, vers, mode, atime, mtime, length = struct.unpack('<IIIIII', b[84:108])
    return name, uid, gid, path, mode, mtime, length


def readdir(c, fid):
    out, off = [], 0
    while True:
        m, r = c.rpc(Tread, struct.pack('<HIIH', fid, off, 0, 8192 // DIRLEN * DIRLEN))
        data = r[8:]
        if not data:
            return out
        for i in range(0, len(data), DIRLEN):
            out.append(dirent(data[i:i + DIRLEN]))
        off += len(data)


def walk(c, listfile):
    want = {}
    for line in open(listfile):
        p, n = line.rsplit(' ', 1)
        want[p] = int(n)
    got = {}

    def visit(path):
        # a fresh fid from the root for each directory: 9P clones only
        # unopened fids
        c.rpc(Tclone, struct.pack('<HH', 1, 999))
        for comp in path.split('/')[1:]:
            c.rpc(Twalk, struct.pack('<H', 999) + s(comp, NAMELEN))
        c.rpc(Topen, struct.pack('<HB', 999, 0))
        ents = readdir(c, 999)
        c.rpc(Tclunk, struct.pack('<H', 999))
        for name, uid, gid, qpath, mode, mtime, length in ents:
            p = path + '/' + name
            got[p] = -1 if mode & CHDIR else length
        for name, uid, gid, qpath, mode, mtime, length in ents:
            if mode & CHDIR:
                visit(path + '/' + name)

    visit('')
    missing = sorted(p for p in want if p not in got)
    # files the administration changes after provisioning (authinit.rc:
    # kfscmd newuser, auth/adduser through keyfs): reported, not failed
    admin = ('/adm/keys', '/adm/users')
    wrong = sorted(p for p in want if p in got and got[p] != want[p]
                   and p not in admin)
    for p in admin:
        if p in got and p in want and got[p] != want[p]:
            print('  administered %s server %d release %d' % (p, got[p], want[p]))
    # keyfs must never show through the served tree (serve.rc)
    leak = sorted(p for p in got if p.startswith('/mnt/keys/')
                  or p.startswith('/mnt/netkeys/'))
    for p in leak:
        print('  LEAK keyfs entry served:', p)
    wrong += leak
    extra = sorted(p for p in got if p not in want)
    print('walk: server has %d paths, list %d; missing %d, length differs %d, extra %d'
          % (len(got), len(want), len(missing), len(wrong), len(extra)))
    for p in missing[:20]:
        print('  missing', p)
    for p in wrong[:20]:
        print('  length', p, 'server', got[p], 'list', want[p])
    # extras: the service's binds (/bin, /dev, /net) and files the
    # server wrote; list files outside the bind points, count the rest
    groups = {}
    for p in extra:
        top = p.split('/')[1]
        if top in ('bin', 'dev', 'net'):
            groups[top] = groups.get(top, 0) + 1
        else:
            print('  extra', p, got[p])
    for top in sorted(groups):
        print('  extra under /%s (bound in by the service): %d' % (top, groups[top]))
    return not missing and not wrong


def main():
    host, port, tree = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    args = sys.argv[4:]
    walklist = None
    if args[:1] == ['--walk']:
        walklist, args = args[1], args[2:]
    paths = args or ['lib/ndb/local']
    c = Conn(host, port)
    # TREE is the host copy of the release: a directory, or the tarball
    # itself (needed for names that differ only in case)
    tar = tar_top = None
    if tree.endswith('.tar.bz2'):
        tar = tarfile.open(tree, 'r:bz2')
        tar_top = tar.next().name.split('/')[0]

    def show(name, m, r):
        print('%-8s T %s' % (name, m.hex()[:64] + ('...' if len(m) > 32 else '')))
        print('%-8s R %s' % ('', r.hex()[:64] + ('...' if len(r) > 32 else '')))

    m, r = c.rpc(Tnop, tag=NOTAG)
    show('Tnop', m, r)
    m, r = c.rpc(Tsession, tag=NOTAG)
    show('Tsession', m, r)
    m, r = c.rpc(Tattach, struct.pack('<H', 1) + s('none', NAMELEN) + s('', NAMELEN) + bytes(28))
    show('Tattach', m, r)
    print('root qid path 0x%x vers %d' % c.qid(r))

    # the root directory: clone, open, read DIRLEN records
    c.rpc(Tclone, struct.pack('<HH', 1, 2))
    c.rpc(Topen, struct.pack('<HB', 2, 0))
    names = []
    off = 0
    while True:
        m, r = c.rpc(Tread, struct.pack('<HIIH', 2, off, 0, 8192 // DIRLEN * DIRLEN))
        data = r[8:]
        if not data:
            break
        for i in range(0, len(data), DIRLEN):
            names.append(dirent(data[i:i + DIRLEN]))
        off += len(data)
    c.rpc(Tclunk, struct.pack('<H', 2))
    print('/ has %d entries:' % len(names))
    for n, uid, gid, path, mode, mtime, length in names:
        print('  %s%s %s %s %d' % (n, '/' if mode & CHDIR else '', uid, gid, length))

    ok = True
    fid = 10
    for p in paths:
        fid += 1
        c.rpc(Tclone, struct.pack('<HH', 1, fid))
        for comp in p.split('/'):
            c.rpc(Twalk, struct.pack('<H', fid) + s(comp, NAMELEN))
        m, r = c.rpc(Tstat, struct.pack('<H', fid))
        st = dirent(r[5:5 + DIRLEN])
        c.rpc(Topen, struct.pack('<HB', fid, 0))
        got = b''
        while True:
            m, r = c.rpc(Tread, struct.pack('<HIIH', fid, len(got), 0, 8192))
            if len(r) == 8:
                break
            got += r[8:]
        c.rpc(Tclunk, struct.pack('<H', fid))
        if tar:
            try:
                want = tar.extractfile('%s/%s' % (tar_top, p)).read()
            except KeyError:
                want = None
        else:
            hp = '%s/%s' % (tree, p)
            want = open(hp, 'rb').read() if os.path.exists(hp) else None
        if want is None:
            # written by the server (e.g. adm/mkext.log): show it
            print('%s: Tstat %s %s %s mode %o length %d; not in the release; contents %r'
                  % (p, st[0], st[1], st[2], st[4], st[6], got[:400]))
            continue
        same = got == want
        ok &= same
        print('%s: Tstat %s %s %s mode %o length %d; read %d bytes; %s host copy'
              % (p, st[0], st[1], st[2], st[4], st[6], len(got),
                 'identical to' if same else 'DIFFERS FROM'))
    if walklist:
        ok &= walk(c, walklist)
    c.rpc(Tclunk, struct.pack('<H', 1))
    print('PASS' if ok else 'FAIL')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
