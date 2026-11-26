#!/usr/bin/env python3
"""Build a card image for the FEP emulator (bsv/PimmFepEmu.bsv): the
files the FEP serves, in a format of OURS.

    python3 tools/mkfepcard.py OUT.img --held
        the held pimos.ipl (docs/nonlocal/pimosobj.tar.Z, object/pimos.ipl)
        and every file it names (the card for the real IPL), then every
        other file of the held object/ directory as pimos:NAME (the
        kernel's files, as ref/pimm/longrun_ipl.kernel_file serves them:
        pimos.conf, pimos.logins, pimos.groups, ...), and the home
        directory's (longrun_ipl.HOME_FILES: the primer's sample1.kl1
        and, since R8, the pkl1 samples (four, then all eight on
        2026-11-26) and their NAME_r8.kl1 adaptations; each with its
        pathname and attributes)
    python3 tools/mkfepcard.py OUT.img --made-up NAME [NAME ...]
        ref/pimm/ref_scsi.py's made-up pimos.ipl listing these .sav files,
        and the files (what ref_scsi.py's parts use)
    python3 tools/mkfepcard.py OUT.img ... --decoys
        and, AHEAD of the real entries, names that are a prefix or an
        extension of a real one, with other contents (test only: a lookup
        that is not exact answers from a decoy)
    python3 tools/mkfepcard.py OUT.img ... --file PATH=HOSTFILE
        and any host file, under the path the IPL will ask for
    python3 tools/mkfepcard.py --list IMG
        the directory of an image

It writes an IMAGE FILE and nothing else.  It refuses a path under /dev
and anything that is not a regular file (a block or character device):
putting the image on a card is the owner's step, with dd (bsv/README.md
"FEP emulator"), never this tool's.

The format, ALL OURS (no FEP disk format is held; the real FEP kept
PIMOS's files in SIMPOS's file system on a PSI disk):

  512-byte blocks, numbers big-endian 32-bit.
  block 0, the header:
     0  magic "PIMFEPC1"
     8  entry count
    12  first directory block (1)
    16  directory blocks
    20  entry size (256)
    24  blocks in the image
    28  0
    32  the attributes: first block, 36 length in bytes (0 0: none)
    40  the script: first block, 44 length in bytes (0 0: none)
    48  0 ...
    64  text: what made the image (for a person with a hex dump)
  blocks 1.., the directory: entries of 256 bytes, two a block:
     0  name length in bytes (at most 224)
     4  first block of the file
     8  length of the file in bytes
    12  the sum of the file's bytes, modulo 2**32 (the board's self-test
        checks it; the emulator does not read it)
    16  the name: the path's bytes EXACTLY as the IPL puts them in
        read_open (fep#read_open 201, argument 4): 16-bit JIS, high byte
        first, as ref_scsi.py's open_file receives them.  The emulator
        compares bytes; no JIS table in hardware.  Zeros after.
        (2026-11-25, R7, ls) bit 31 of the name length set: a DIRECTORY
        (fep.py 204, Fep.list_dir), the name its path as 204 gives it,
        the "file" 237's answer for fep.LISTING_WILDCARD (fep.listing);
        read_open does not find it, 204 finds nothing else
   240  the file's pathname, 221's answer string: first block, 244
        length in bytes; 248 its attributes, 222's: first block, 252
        length (2026-11-25, a home file, fep.FileData: the bytes fep.py
        answers, fep.jis(pathname) and fep.attribute_string).  0 0 for
        a file that has neither (every pimos: file, every .sav), on
        which 221 and 222 are refused as fep.py refuses them.
  then the files, each from a block boundary, in directory order, the
  last block zero-padded, a file's pathname and attributes after it,
  each from a block boundary; then the attributes and the script, each
  from a block boundary.

fep.py's constants, on every card this tool or bsv/fepemu_check.py
makes (fep_tables), so the emulator holds none of them in hardware:
  the attributes  fep_attributes' (240) whole reply message,
                  fep.pack_message([fep.NORMAL] + fep.ATTRIBUTES)
  the script      fep.Fep().script, the events Fep.idle() takes in
                  order: per event the kind (SCRIPT_KINDS: login 1, getl
                  2), the length of the reply's string, the string
                  (login: fep.login_record; getl: fep.jis of the line),
                  zeros to four bytes.  An event kind not in SCRIPT_KINDS
                  stops the tool.

Names and contents are those ref/pimm/ref_scsi.py's open_file gives:
"pimos:pimos.ipl" for the list, and ">sys>csp>PIMOS.DIR>NAME" for a .sav
file, whose bytes are ref/pimm/lockstep_file.file_words(NAME) (the held
object archive), packed big-endian.
"""
import os
import stat
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'ref', 'pimm'))
sys.path.insert(0, os.path.join(HERE, '..', 'asm'))

MAGIC = b'PIMFEPC1'
BLOCK, ENTRY, NAME_MAX = 512, 256, 224


def sum32(data):
    return sum(data) & 0xffffffff


def jis_bytes(text):
    import lockstep_cons as cons
    return struct.pack('>%dH' % len(text), *cons.jis(text))


def name_text(raw):
    import lockstep_cons as cons
    try:
        return cons.ascii_of(struct.unpack('>%dH' % (len(raw) // 2), raw))
    except (KeyError, struct.error):
        return '(hex) ' + raw.hex()


def made_up(names):
    """[(path bytes, contents)] for ref_scsi.py's parts."""
    import ref_scsi as rs
    out = [(jis_bytes(rs.LIST), rs.listing(names))]
    for n in names:
        out.append((jis_bytes(rs.DIR + n), rs.words_bytes(rs.lfile.file_words(n))))
    return out


def held():
    """[(path bytes, contents)]: the held pimos.ipl and its files, then
    the rest of the held object directory as pimos:NAME."""
    import ref_scsi as rs
    words = rs.ipll.list_words()
    out = [(jis_bytes(rs.LIST), rs.words_bytes(words))]
    for entry in rs.ipll.by_hand(words):
        path = rs.cons.ascii_of(entry)
        if not path.startswith(rs.DIR):
            raise SystemExit('mkfepcard: the held list names %r, not under %s' % (path, rs.DIR))
        out.append((rs.words_bytes(list(entry)),
                    rs.words_bytes(rs.lfile.file_words(path[len(rs.DIR):]))))
    have = dict(out)
    for name, data in objects():
        if name in have:
            # object/pimos.ipl is the list already put first
            if have[name] != data:
                raise SystemExit('mkfepcard: %s differs from the held list' % name_text(name))
            continue
        out.append((name, data))
    return out


class DirEntry(bytes):
    """A directory's entry: its data is 237's answer (fep.listing)."""


def dirs():
    """[(path bytes, DirEntry)]: the directories 204 opens
    (longrun_ipl.home_listing; R7, ls, 2026-11-25): the home."""
    import longrun_ipl as lr
    path = jis_bytes(lr.HOME)
    return [(path, DirEntry(lr.home_listing(path)))]


def objects():
    """[(path bytes, contents)]: every file of the held object directory
    (docs/nonlocal/pimosobj.tar.Z, object/) as pimos:NAME, the kernel's
    file service (ref/pimm/longrun_ipl.kernel_file: object/INSTALL copies
    object/* to pimos:)."""
    import longrun_ipl as lr
    lr.held_object('')
    return [(jis_bytes('pimos:' + n), lr._held[n]) for n in sorted(lr._held)] + homes() + dirs()


def homes():
    """[(path bytes, fep.FileData)]: the home directory's files
    (longrun_ipl.HOME_FILES: the primer's sample1.kl1, 2026-11-25; the
    pkl1 samples and their adaptations, R8), as
    HOME>NAME, with what 221 and 222 answer for each."""
    import longrun_ipl as lr
    return [(jis_bytes(lr.HOME + '>' + n), lr.home_file(n)) for n in sorted(lr.HOME_FILES)]


def info(data):
    """(221's answer bytes, 222's) of a file, b'' b'' for one that has
    neither (plain bytes)"""
    import fep
    if isinstance(data, fep.FileData):
        return fep.jis(data.pathname), bytes(data.attributes)
    return b'', b''


# the event kinds of fep.Fep.script, as the emulator's held requests
# name them (bsv/PimmFepEmu.bsv heldLogin, heldGetl)
SCRIPT_KINDS = {'login': 1, 'getl': 2}


def fep_tables(events=None):
    """(attributes, script): fep.py's constants as the card holds them
    (the header above); events, a script in place of fep.Fep().script
    (a test tape's)."""
    import fep
    attributes = fep.pack_message([fep.NORMAL] + fep.ATTRIBUTES)
    script = b''
    for kind, what in (fep.Fep(None).script if events is None else events):
        if kind not in SCRIPT_KINDS:
            raise SystemExit('mkfepcard: fep.py\'s script has a %r event: give it a code in '
                             'SCRIPT_KINDS and the emulator the hold that waits for it' % kind)
        data = fep.login_record(**what) if kind == 'login' else fep.jis(what)
        script += struct.pack('>II', SCRIPT_KINDS[kind], len(data)) + data
        script += bytes(-len(data) % 4)
    return attributes, script


def decoys(entries):
    """A prefix (one character short) and an extension (one more) of
    each real name, with contents that are not the file's."""
    out = []
    for name, _ in entries:
        for k, alt in (('prefix', name[:-2]), ('extension', name + jis_bytes('x'))):
            body = ('DECOY %s of %s\n' % (k, name_text(name))).encode()
            body += bytes(len(body) % 2)
            out.append((alt, DirEntry(body) if isinstance(_, DirEntry) else body))
    return out


def build(entries, note, tables=None):
    """The image; tables (attributes, script) as fep_tables() gives, or
    None for neither."""
    names = [n for n, _ in entries]
    if len(set(names)) != len(names):
        raise SystemExit('mkfepcard: a name twice')
    for n in names:
        if not 0 < len(n) <= NAME_MAX:
            raise SystemExit('mkfepcard: a name of %d bytes (1..%d)' % (len(n), NAME_MAX))
    per = BLOCK // ENTRY
    dir_blocks = max(1, -(-len(entries) // per))
    at = 1 + dir_blocks
    directory, files = b'', b''
    for name, data in entries:
        flag = 1 << 31 if isinstance(data, DirEntry) else 0
        entry = struct.pack('>IIII', len(name) | flag, at, len(data), sum32(data))
        entry += name + bytes(240 - 16 - len(name))
        files += data + bytes(-len(data) % BLOCK)
        at += -(-len(data) // BLOCK)
        for t in info(data):
            entry += struct.pack('>II', at if t else 0, len(t))
            files += t + bytes(-len(t) % BLOCK)
            at += -(-len(t) // BLOCK)
        directory += entry
    directory += bytes(dir_blocks * BLOCK - len(directory))
    where = []
    for t in tables or (b'', b''):
        where += [at if t else 0, len(t)]
        files += t + bytes(-len(t) % BLOCK)
        at += -(-len(t) // BLOCK)
    head = MAGIC + struct.pack('>IIIIII', len(entries), 1, dir_blocks, ENTRY, at, 0)
    head += struct.pack('>IIII', *where)
    head += bytes(64 - len(head)) + note.encode()[:BLOCK - 64]
    head += bytes(BLOCK - len(head))
    img = head + directory + files
    assert len(img) == at * BLOCK
    return img


def parse(img):
    """-> (header dict, [entry dict]) of an image's bytes; raises on a bad one."""
    if img[:8] != MAGIC:
        raise ValueError('no magic %r' % MAGIC)
    count, first, nblocks, esize, total, _ = struct.unpack('>IIIIII', img[8:32])
    if esize != ENTRY:
        raise ValueError('entry size %d' % esize)
    out = []
    for i in range(count):
        e = img[first * BLOCK + i * ENTRY:][:ENTRY]
        nl, start, length, s = struct.unpack('>IIII', e[:16])
        isdir, nl = bool(nl >> 31), nl & 0x7fffffff
        pb, pl, ab, al = struct.unpack('>IIII', e[240:256])
        data = img[start * BLOCK:start * BLOCK + length]
        out.append(dict(name=e[16:16 + nl], start=start, length=length, sum=s, dir=isdir,
                        ok=len(data) == length and sum32(data) == s, data=data,
                        pathname=img[pb * BLOCK:pb * BLOCK + pl] if pb else b'',
                        attributes=img[ab * BLOCK:ab * BLOCK + al] if ab else b''))
    note = img[64:BLOCK].rstrip(b'\0').decode(errors='replace')
    ab, al, sb, sl = struct.unpack('>IIII', img[32:48])
    return dict(count=count, first=first, blocks=nblocks, total=total, note=note,
                attributes=img[ab * BLOCK:ab * BLOCK + al], script=img[sb * BLOCK:sb * BLOCK + sl],
                tables=(ab, al, sb, sl)), out


def safe_output(path):
    real = os.path.realpath(path)
    if real.startswith('/dev/') or path.startswith('/dev/'):
        raise SystemExit('mkfepcard: refusing %s: this tool writes image files only '
                         '(flashing a card is the owner\'s dd step)' % path)
    if os.path.exists(real) and not stat.S_ISREG(os.stat(real).st_mode):
        raise SystemExit('mkfepcard: refusing %s: not a regular file' % path)


def list_image(path):
    with open(path, 'rb') as fh:
        img = fh.read()
    h, entries = parse(img)
    print('%s: %d entries, directory blocks %d..%d, %d blocks (%d bytes)'
          % (path, h['count'], h['first'], h['first'] + h['blocks'] - 1, h['total'],
             h['total'] * BLOCK))
    print('  note: %s' % h['note'])
    ab, al, sb, sl = h['tables']
    print('  attributes: block %d, %d bytes; script: block %d, %d bytes' % (ab, al, sb, sl))
    print('  %-6s %-9s %-9s %-8s %s' % ('entry', 'block', 'bytes', 'sum32', 'name'))
    bad = 0
    for i, e in enumerate(entries):
        print('  %-6d %-9d %-9d %08x %s%s%s%s' % (i, e['start'], e['length'], e['sum'],
                                               name_text(e['name']),
                                               '   (a directory: 237)' if e['dir'] else '',
                                               '' if e['ok'] else '   BAD (sum or length)',
                                               '   (221: %s; 222: %d bytes)'
                                               % (name_text(e['pathname']), len(e['attributes']))
                                               if e['pathname'] or e['attributes'] else ''))
        bad += not e['ok']
    return 1 if bad else 0


def main(argv):
    if '--list' in argv:
        return list_image(argv[argv.index('--list') + 1])
    if len(argv) < 3:
        print(__doc__)
        return 2
    out = argv[1]
    safe_output(out)
    entries = []
    if '--held' in argv:
        entries = held()
    if '--made-up' in argv:
        i = argv.index('--made-up') + 1
        names = []
        while i < len(argv) and not argv[i].startswith('--'):
            names.append(argv[i])
            i += 1
        entries += made_up(names)
    for i, a in enumerate(argv):
        if a == '--file':
            name, host = argv[i + 1].split('=', 1)
            with open(host, 'rb') as fh:
                entries.append((jis_bytes(name), fh.read()))
    if not entries:
        raise SystemExit('mkfepcard: nothing to put on the card')
    if '--decoys' in argv:
        entries = decoys(entries) + entries
    note = 'PIM/m FEP card (OURS), pim/tools/mkfepcard.py %s' % ' '.join(argv[2:])
    tables = fep_tables()
    img = build(entries, note, tables)
    tmp = out + '.tmp'
    with open(tmp, 'wb') as fh:
        fh.write(img)
    os.replace(tmp, out)
    h, got = parse(img)
    assert [e['name'] for e in got] == [n for n, _ in entries]
    assert all(e['ok'] and e['data'] == d and (e['pathname'], e['attributes']) == info(d)
               and e['dir'] == isinstance(d, DirEntry) for e, (_, d) in zip(got, entries))
    assert (h['attributes'], h['script']) == tables
    print('mkfepcard: wrote %s, %d entries, %d bytes' % (out, len(entries), len(img)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
