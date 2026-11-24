"""Disassemble functions of a Hobbit BeBox kernel (big-endian ELF, machine
0x39D) by symbol name, with asm/hobbit_asm.py.  Read-only.  Evidence tool
for docs/bebox_hardware.md (tag [K]).

  python3 -I tools/bebox_kdis.py asm KERNEL name [name ...]

A symbol of size 0 is shown as 46 bytes.
"""
import re
import struct
import sys

sys.path.insert(0, sys.argv[1])
import hobbit_asm  # noqa: E402

data = open(sys.argv[2], 'rb').read()
e = '>'
phoff, = struct.unpack(e + 'I', data[28:32])
phentsize, phnum = struct.unpack(e + 'HH', data[42:46])
segs = []
for i in range(phnum):
    o = phoff + i * phentsize
    segs.append(struct.unpack(e + 'IIIIIIII', data[o:o + 32]))
shoff, = struct.unpack(e + 'I', data[32:36])
shentsize, shnum = struct.unpack(e + 'HH', data[46:50])
secs = [struct.unpack(e + 'IIIIIIIIII', data[shoff + i * shentsize:shoff + i * shentsize + 40])
        for i in range(shnum)]
syms = {}
rev = {}
for s in secs:
    if s[1] == 2:
        so = secs[s[6]][4]
        for k in range(s[5] // 16):
            o = s[4] + k * 16
            name, value, size, info, other, shndx = struct.unpack(e + 'IIIBBH', data[o:o + 16])
            n = data[so + name:data.index(b'\0', so + name)].decode('latin-1')
            if value:
                syms[n] = (value, size)
                rev.setdefault(value, n)


def fo(va):
    for (t, off, v, p, fs, ms, fl, al) in segs:
        if v <= va < v + fs:
            return off + va - v
    raise KeyError(hex(va))


def sub(m):
    v = int(m.group(0), 16)
    return m.group(0) + ('<' + rev[v] + '>' if v in rev else '')


for name in sys.argv[3:]:
    a, size = syms[name]
    if size == 0:
        size = 46
    off = fo(a)
    raw = data[off:off + size]
    parcels = [int.from_bytes(raw[i:i + 2], 'big') for i in range(0, len(raw) - 1, 2)]
    print('==', name, hex(a), size)
    try:
        lines = hobbit_asm.disassemble_parcels(parcels)
    except Exception as ex:
        print('  disassembly failed:', ex)
        continue
    pc = a
    for L in lines:
        n = 1 if not L.startswith('.') else int(L[1])
        L = re.sub(r'0x[0-9a-f]{7,8}', sub, L)
        m = re.search(r'CALL (-?0x[0-9a-f]+)$', L)
        if m:
            t = a + int(m.group(1), 16)
            L += '   ; -> %s' % rev.get(t, hex(t))
        print('%08x +%-4x %s' % (pc, pc - a, L))
        pc += 2 * n
