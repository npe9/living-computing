#!/usr/bin/env python3
"""Read and disassemble the Hobbit BeBox's ELF executables (docs/bebox_hobbit.md).

Be's 1993-94 kernels and programs are big-endian ELF32 files with
e_machine 0x39d (AT&T Hobbit, MetaWare High C `hc`), statically linked,
mostly with a symbol table.  Text is a sequence of 16-bit parcels, the
earlier parcel in the more significant half of each big-endian word.

The files are untrusted data: run this with `python3 -I`.

  python3 -I tools/beelf.py KERNEL --headers
  python3 -I tools/beelf.py KERNEL --syms [REGEX]
  python3 -I tools/beelf.py KERNEL --dis NAME|0xADDR [COUNT]   # disassemble
  python3 -I tools/beelf.py KERNEL --refs 0xADDR [0xHI]        # constants in range
"""
import bisect
import os
import re
import struct
import sys

H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(H, "asm"))
import hobbit_asm  # noqa: E402

EM_HOBBIT = 0x39D
CPU_PARCEL = (0x0B << 10) | hobbit_asm.NILADICS["CPU"][0]


class ElfError(Exception):
    pass


class Elf:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.blob = d = f.read()
        if d[:4] != b"\x7fELF" or d[4] != 1 or d[5] != 2:
            raise ElfError("%s: not a big-endian ELF32 file" % path)
        (self.type, self.machine, _ver, self.entry, phoff, shoff, _flags,
         _ehs, phes, phn, shes, shn, shstr) = struct.unpack(">HHIIIIIHHHHHH", d[16:52])
        if self.machine != EM_HOBBIT:
            raise ElfError("%s: e_machine 0x%x, not the Hobbit's 0x39d"
                           % (path, self.machine))
        self.segments = []      # (vaddr, filesz, memsz, offset, flags)
        for i in range(phn):
            p = struct.unpack(">8I", d[phoff + i * phes: phoff + i * phes + 32])
            if p[0] == 1:
                self.segments.append((p[2], p[4], p[5], p[1], p[6]))
        secs = [struct.unpack(">10I", d[shoff + i * shes: shoff + i * shes + 40])
                for i in range(shn)]
        self.sections = {}
        if secs:
            so = secs[shstr][4]
            for s in secs:
                self.sections[self._str(so, s[0])] = s
        self.symbols = []       # (value, size, kind, name); kind T/D/B/?
        if ".symtab" in self.sections and ".strtab" in self.sections:
            sym = self.sections[".symtab"]
            stro = self.sections[".strtab"][4]
            text = self.sections.get(".text")
            for i in range(sym[5] // 16):
                name, value, size, info, _other, shndx = struct.unpack(
                    ">IIIBBH", d[sym[4] + 16 * i: sym[4] + 16 * i + 16])
                n = self._str(stro, name)
                if not n or (info & 0xF) in (3, 4):     # section, file
                    continue
                kind = "T" if (info & 0xF) == 2 else "D"
                if text and text[3] <= value < text[3] + text[5]:
                    kind = "T"
                self.symbols.append((value, size, kind, n))
        self.symbols.sort()
        self.text_syms = [(v, n) for v, s, k, n in self.symbols if k == "T"]
        self._addrs = [v for v, n in self.text_syms]
        self.by_name = {}
        for v, s, k, n in self.symbols:
            self.by_name.setdefault(n, v)

    def _str(self, base, off):
        e = self.blob.index(b"\0", base + off)
        return self.blob[base + off:e].decode("latin-1")

    def words(self):
        """{address: big-endian word} of every loadable byte (BSS as 0)."""
        out = {}
        for vaddr, filesz, memsz, off, _fl in self.segments:
            data = self.blob[off:off + filesz] + b"\0" * (memsz - filesz)
            if vaddr & 3:
                raise ElfError("segment at 0x%x is not word aligned" % vaddr)
            data += b"\0" * (-len(data) % 4)
            for i in range(0, len(data), 4):
                out[vaddr + i] = int.from_bytes(data[i:i + 4], "big")
        return out

    def byte_at(self, va):
        for vaddr, filesz, memsz, off, _fl in self.segments:
            if vaddr <= va < vaddr + filesz:
                return self.blob[off + va - vaddr]
        return None

    def cstring(self, va, limit=512):
        s = bytearray()
        while len(s) < limit:
            b = self.byte_at(va + len(s))
            if not b:
                break
            s.append(b)
        return s.decode("latin-1")

    def parcel(self, va):
        return (self.byte_at(va) << 8) | self.byte_at(va + 1)

    def func(self, pc):
        i = bisect.bisect_right(self._addrs, pc) - 1
        if i < 0:
            return "?", 0
        return self.text_syms[i][1], self.text_syms[i][0]

    def where(self, pc):
        n, b = self.func(pc)
        return "%s+0x%x" % (n, pc - b)

    def func_end(self, start):
        i = bisect.bisect_right(self._addrs, start)
        if i < len(self._addrs):
            return self._addrs[i]
        text = self.sections[".text"]
        return text[3] + text[5]

    def disassemble(self, start, end):
        """[(address, text)] for the parcels in [start, end)."""
        out = []
        pc = start
        cpu = False
        while pc < end:
            p0 = self.parcel(pc)
            # Length from the first parcel (PRM Table 1-14): bit 15 clear,
            # one parcel; 10, three; 11, five.
            n = 1 if not p0 & 0x8000 else (3 if p0 >> 14 == 2 else 5)
            ps = [self.parcel(pc + 2 * i) for i in range(n)]
            # A CPU escape changes how mode 7 decodes (p. 3-14): decode
            # the instruction after one with the escape in front.
            lines = hobbit_asm.disassemble_parcels(([CPU_PARCEL] if cpu else []) + ps)
            line = lines[-1]
            cpu = p0 == CPU_PARCEL
            # PC-relative targets are printed as the instruction's own
            # offset in the list given (pc 2 after an escape): relocate.
            m = re.match(r"(\.\d )?(CALL|JMP\w*|LDRAA) (-?0x[0-9a-f]+)$", line)
            if m:
                target = (pc + int(m.group(3), 16) - (2 if len(lines) == 2 else 0)) & 0xFFFFFFFF
                line = "%s%s 0x%08x" % (m.group(1) or "", m.group(2), target)
            out.append((pc, line))
            pc += 2 * n
        return out


def _name_consts(elf, text):
    def sub(m):
        v = int(m.group(0), 16)
        for val, _s, _k, n in elf.symbols:
            if val == v:
                return m.group(0) + "<" + n + ">"
        return m.group(0)
    return re.sub(r"0x[0-9a-f]{7,8}", sub, text)


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    e = Elf(argv[1])
    op = argv[2]
    if op == "--headers":
        print("entry 0x%08x machine 0x%x" % (e.entry, e.machine))
        for vaddr, filesz, memsz, off, fl in e.segments:
            print("LOAD vaddr 0x%08x filesz 0x%x memsz 0x%x off 0x%x flags %d"
                  % (vaddr, filesz, memsz, off, fl))
        for name, s in e.sections.items():
            if name:
                print("%-10s addr 0x%08x size 0x%x" % (name, s[3], s[5]))
        print("%d symbols" % len(e.symbols))
    elif op == "--syms":
        pat = re.compile(argv[3]) if len(argv) > 3 else None
        for v, s, k, n in e.symbols:
            if pat is None or pat.search(n):
                print("%08x %6d %s %s" % (v, s, k, n))
    elif op == "--dis":
        target = argv[3]
        if target.startswith("0x"):
            start = int(target, 16)
            end = start + 2 * int(argv[4] if len(argv) > 4 else 64)
        else:
            start = e.by_name[target]
            end = e.func_end(start)
        for pc, line in e.disassemble(start, end):
            print("%08x %-22s %s" % (pc, e.where(pc), _name_consts(e, line)))
    elif op == "--refs":
        lo = int(argv[3], 16)
        hi = int(argv[4], 16) if len(argv) > 4 else lo + 1
        for pc, func, line, v in refs(e, lo, hi):
            print("%08x %-28s 0x%08x  %s" % (pc, func, v, line))
    elif op == "--str":
        for a in argv[3:]:      # ADDR, or PC+OFFSET (an LDRAA's operand)
            va = sum(int(x, 16) for x in a.split("+")) & 0xFFFFFFFF
            print("0x%08x %r" % (va, e.cstring(va)))
    elif op == "--words":
        va = int(argv[3], 16)
        for i in range(int(argv[4]) if len(argv) > 4 else 16):
            a = va + 4 * i
            w = int.from_bytes(bytes(e.byte_at(a + j) or 0 for j in range(4)), "big")
            print("0x%08x 0x%08x %s" % (a, w, e.where(w) if e.text_syms and
                                         e.text_syms[0][0] <= w < e.func_end(e.text_syms[-1][0]) else ""))
    elif op == "--unimpl":
        for pc, func, line in sweep(e):
            if "unimplemented" in line or line.startswith("??"):
                print("%08x %-28s %s" % (pc, func, line))
    else:
        print(__doc__, file=sys.stderr)
        return 2
    return 0


NUMBER = re.compile(r"(?<![\w])(-?0x[0-9a-f]+|-?\d+)")


def sweep(e):
    """Every instruction of every text symbol: (pc, where, text)."""
    for i, (start, name) in enumerate(e.text_syms):
        end = e.func_end(start)
        if end - start > 0x20000:
            continue
        for pc, line in e.disassemble(start, end):
            yield pc, "%s+0x%x" % (name, pc - start), line


def refs(e, lo, hi):
    """Instructions with a constant operand in [lo, hi): (pc, where, text, value)."""
    for pc, where, line in sweep(e):
        body = line.split(" ", 1)[1] if line.startswith(".") else line
        if " " not in body:
            continue
        for tok in NUMBER.findall(body.split(" ", 1)[1]):
            v = int(tok, 0) & 0xFFFFFFFF
            if lo <= v < hi:
                yield pc, where, line, v


if __name__ == "__main__":
    sys.exit(main(sys.argv))
