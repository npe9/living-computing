#!/usr/bin/env python3
"""Read Be Inc.'s 1993-94 file system (version 1.0) on Hobbit BeBox disks.

This is the file system of the AT&T Hobbit BeBox prototypes' disks and
floppies (docs/bebox_hobbit.md), not the later BFS.  The layout below is
the one the MIT-licensed BeBox emulator documents in its
src/core/hobbit/HobbitVolume.h (github.com/johnrash/bebox, read
2026-11-24); this reader is written from that description and checked on
the surviving images (`--list`), not copied.

  sector 0 (volume header, big endian): 0x00 version 0x00010000,
    0x04 creation time, 0x08 first bitmap sector, 0x0c bitmap sectors,
    0x10 root directory sector, 0x14 total sectors, 0x18 bytes/sector
    (512), 0x2c volume name (32 bytes).
  directory: chain of 4 KB blocks; a 64-byte header whose word 0 is the
    next block's sector (0 ends), then 63 64-byte entries: name[32],
    first sector, sector count, type (0xffffffff = directory), created,
    modified, size, (0x38 unknown), creator.  first == 0: free;
    name[0] == 0: deleted.
  file data: first with bit 31 set = contiguous from (first & 0x7fffffff);
    otherwise first is a map sector: next map, first logical sector, then
    up to 63 (sector, count) extents ending at sector 0xffffffff; empty
    extents are skipped.

The images are untrusted data: run this with `python3 -I`.

  python3 -I tools/befs1.py IMAGE --list [PATH]       # recursive listing
  python3 -I tools/befs1.py IMAGE --get PATH OUTFILE  # extract one file
  python3 -I tools/befs1.py IMAGE --header
"""
import struct
import sys

SECTOR = 512
DIRECTORY = 0xFFFFFFFF


class BefsError(Exception):
    pass


class Entry:
    __slots__ = ("name", "first", "count", "type", "created", "modified",
                 "size", "creator")

    def __init__(self, raw):
        self.name = raw[:32].split(b"\0", 1)[0].decode("latin-1")
        (self.first, self.count, self.type, self.created, self.modified,
         self.size, _unknown, self.creator) = struct.unpack(">8I", raw[32:64])

    @property
    def is_dir(self):
        return self.type == DIRECTORY


class Volume:
    def __init__(self, path):
        # A path, or a file object (beboot's disk with its write overlay).
        self.f = open(path, "rb") if isinstance(path, str) else path
        self.f.seek(0, 2)
        self.image_size = self.f.tell()
        h = self.sectors(0, 1, check=False)
        (self.version, self.created, self.bitmap, self.bitmap_count,
         self.root, self.total, self.bps) = struct.unpack(">7I", h[:28])
        self.name = h[0x2C:0x4C].split(b"\0", 1)[0].decode("latin-1")
        if (self.version != 0x00010000 or self.bps != SECTOR or not self.root
                or self.root >= self.total
                or self.total * SECTOR > self.image_size + SECTOR):
            raise BefsError("%s: not a version 1.0 Be file system volume" % path)

    def sectors(self, sector, count, check=True):
        if check and (sector == 0 or sector + count > self.total):
            raise BefsError("sector range %d+%d outside the volume" % (sector, count))
        self.f.seek(sector * SECTOR)
        data = self.f.read(count * SECTOR)
        if len(data) != count * SECTOR:
            raise BefsError("short read at sector %d" % sector)
        return data

    def directory(self, sector):
        out = []
        blocks = 0
        while sector:
            blocks += 1
            if blocks > 4096:
                raise BefsError("directory chain loops")
            block = self.sectors(sector, 8)
            for i in range(63):
                raw = block[64 + 64 * i: 128 + 64 * i]
                e = Entry(raw)
                if e.first == 0 or raw[0] == 0:
                    continue
                out.append(e)
            sector = struct.unpack(">I", block[:4])[0]
        return out

    def lookup(self, path):
        cur = None
        sector = self.root
        for part in [p for p in path.split("/") if p]:
            if cur is not None and not cur.is_dir:
                raise BefsError("%s: not a directory" % path)
            found = [e for e in self.directory(sector) if e.name == part]
            if not found:
                raise BefsError("%s: not found on %s" % (path, self.name))
            cur = found[0]
            sector = cur.first
        return cur

    def read(self, entry):
        if entry.is_dir:
            raise BefsError("%s: a directory" % entry.name)
        n = (entry.size + SECTOR - 1) // SECTOR
        if entry.first & 0x80000000:
            data = self.sectors(entry.first & 0x7FFFFFFF, n) if n else b""
            return data[:entry.size]
        parts = []
        done = 0
        m = entry.first
        maps = 0
        while m and done < n:
            maps += 1
            if maps > 65536:
                raise BefsError("block map loops")
            raw = self.sectors(m, 1)
            for i in range(63):
                start, count = struct.unpack(">II", raw[8 + 8 * i: 16 + 8 * i])
                if start == 0xFFFFFFFF or done >= n:
                    break
                if count == 0:
                    continue
                count = min(count, n - done)
                parts.append(self.sectors(start, count))
                done += count
            m = struct.unpack(">I", raw[:4])[0]
        if done < n:
            raise BefsError("%s: the block map is short" % entry.name)
        return b"".join(parts)[:entry.size]

    def walk(self, sector=None, prefix=""):
        for e in self.directory(self.root if sector is None else sector):
            path = prefix + "/" + e.name
            yield path, e
            if e.is_dir:
                yield from self.walk(e.first, path)


def fourcc(v):
    b = struct.pack(">I", v)
    return b.decode("latin-1") if all(32 <= c < 127 for c in b) else "%08x" % v


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    vol = Volume(argv[1])
    if argv[2] == "--header":
        print("volume %r version %#x total %d sectors root %d bitmap %d+%d created %d"
              % (vol.name, vol.version, vol.total, vol.root, vol.bitmap,
                 vol.bitmap_count, vol.created))
    elif argv[2] == "--list":
        start = None
        prefix = ""
        if len(argv) > 3 and argv[3].strip("/"):
            e = vol.lookup(argv[3])
            start, prefix = e.first, "/" + argv[3].strip("/")
        for path, e in vol.walk(start, prefix):
            kind = "d" if e.is_dir else fourcc(e.type)
            print("%-4s %-8s %10d %10d %s" % (kind[:4] if e.is_dir else kind,
                  fourcc(e.creator), e.size, e.modified, path))
    elif argv[2] == "--get" and len(argv) == 5:
        data = vol.read(vol.lookup(argv[3]))
        with open(argv[4], "wb") as f:
            f.write(data)
        print("%s: %d bytes" % (argv[3], len(data)))
    else:
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
