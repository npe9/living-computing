"""List an ELF file's symbols (value, size, name) whose name contains any
of the given substrings.  Read-only.  Evidence tool for
docs/bebox_hardware.md (tag [K]).

  python3 -I tools/bebox_ksyms.py KERNEL substring [substring ...]
"""
import struct
import sys

data = open(sys.argv[1], 'rb').read()
e = '>' if data[5] == 2 else '<'
shoff, = struct.unpack(e + 'I', data[32:36])
shentsize, shnum, shstrndx = struct.unpack(e + 'HHH', data[46:52])
secs = []
for i in range(shnum):
    o = shoff + i * shentsize
    secs.append(struct.unpack(e + 'IIIIIIIIII', data[o:o + 40]))
for s in secs:
    if s[1] == 2:  # SHT_SYMTAB
        strtab = secs[s[6]]
        so = strtab[4]
        for k in range(s[5] // 16):
            o = s[4] + k * 16
            name, value, size, info, other, shndx = struct.unpack(e + 'IIIBBH', data[o:o + 16])
            n = data[so + name:data.index(b'\0', so + name)].decode('latin-1')
            if any(p in n for p in sys.argv[2:]):
                print('%08x %6d %s' % (value, size, n))
