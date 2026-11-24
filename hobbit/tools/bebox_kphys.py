"""Find a Hobbit BeBox kernel's table of physical objects: locate each
name string's virtual address and print the eight words around every
aligned pointer to it ({name, flag, base, size} entries).  Read-only.
Evidence tool for docs/bebox_hardware.md (tag [K]).

  python3 -I tools/bebox_kphys.py KERNEL phram rom io ether_regs ...
"""
import struct
import sys

data = open(sys.argv[1], 'rb').read()
assert data[:4] == b'\x7fELF', 'not ELF'
endian = '>' if data[5] == 2 else '<'
(e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags, e_ehsize,
 e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = struct.unpack(
    endian + 'HHIIIIIHHHHHH', data[16:52])
print('endian', endian, 'machine', hex(e_machine), 'entry', hex(e_entry))
segs = []
for i in range(e_phnum):
    off = e_phoff + i * e_phentsize
    p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = \
        struct.unpack(endian + 'IIIIIIII', data[off:off + 32])
    print('phdr', p_type, hex(p_offset), hex(p_vaddr), hex(p_paddr),
          hex(p_filesz), hex(p_memsz), p_flags)
    segs.append((p_offset, p_vaddr, p_filesz))


def vaddr(fileoff):
    for o, v, s in segs:
        if o <= fileoff < o + s:
            return v + fileoff - o
    return None


def fileoff(va):
    for o, v, s in segs:
        if v <= va < v + s:
            return o + va - v
    return None


names = [n.encode() for n in sys.argv[2:]]
seen = set()
for n in names:
    start = 0
    while True:
        i = data.find(n + b'\0', start)
        if i < 0:
            break
        start = i + 1
        if i > 0 and data[i - 1] != 0:
            continue
        va = vaddr(i)
        if va is None:
            continue
        pat = struct.pack(endian + 'I', va)
        j = 0
        while True:
            j = data.find(pat, j)
            if j < 0:
                break
            if j % 4 == 0 and j not in seen:
                seen.add(j)
                words = struct.unpack(endian + '8I', data[j - 8:j + 24])
                print(n.decode(), 'ptr@', hex(vaddr(j) or 0), ' '.join('%08x' % w for w in words))
            j += 1
