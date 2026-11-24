#!/usr/bin/env python3
"""Load the psdpim PSI-III firmware files in memory (no extraction to disk).

Usage: python3 -I stores.py ARCHIVE   (prints a summary of every PMPSI.DIR member)
Imported by test_layout.py via runpy-free path insertion.
"""
import io
import subprocess
import sys
import tarfile


def members(tar):
    raw = subprocess.run(['gzip', '-dc', tar], stdout=subprocess.PIPE, check=True).stdout
    out = {}
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.isfile() and 'PMPSI.DIR/' in m.name:
                out[m.name.split('PMPSI.DIR/')[1]] = tf.extractfile(m).read()
    return out


def kbn_words(raw):
    """(value, tag) 5-byte words of the .kbn container (as asm/psdpim.py)."""
    size = int.from_bytes(raw[4:6], 'little') | int.from_bytes(raw[6:8], 'little') << 16
    out = []
    body = raw[256:]
    for b in range(0, len(body), 256):
        blk = body[b:b + 256]
        for i in range(51):
            w = blk[i * 5:i * 5 + 5]
            if len(w) == 5:
                out.append((int.from_bytes(w[:4], 'little'), w[4]))
    return out[:size]


def raw64(raw, off=256, order='little'):
    body = raw[off:]
    return [int.from_bytes(body[i:i + 8], order) for i in range(0, len(body) - 7, 8)]


def mekbn_images(raw):
    ws = kbn_words(raw)
    img = lambda base, n: [ws[base + 2 * i][0] | ws[base + 2 * i + 1][0] << 32 for i in range(n)]
    return img(0x900, 0x5800), img(0xba00, 0x6800)


if __name__ == '__main__':
    ms = members(sys.argv[1])
    for k, v in sorted(ms.items()):
        print(k, len(v), v[:16].hex(), ((len(v) - 256) / 8))
