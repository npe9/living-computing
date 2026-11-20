#!/usr/bin/env python3
"""A1: the host side of the 1st Edition Plan 9 syscall shim.

The machine side is a short Hobbit stub the testbench places in the boot
window's Exec header (0x1000..0x101f, never executed by the program);
this file holds the host side: the syscall set (read from the 1e libc
stubs, not guessed), the argument decoder, the file table, the stub's
assembly, and the generator for the `P9Shim` package the testbench
links.

What the hardware does (and this file does not):

  KCALL src      *(ISP-12) = src   the syscall id, PRM p. 3-29
                 *(ISP-8)  = PC
                 *(ISP-4)  = PSW
                 ISP -= 16; PC = *(VB+0); PSW &= 0xFFFF0000

The id lands at `ISP-12`, which is the *doorbell word*: the host polls
it, does the syscall, and clears it.

Host -> machine is two words of the shim's device page, read by the stub
as ordinary absolute-address operands (an operand outside the stack
cache is a word of memory; HobbitCore.bsv, "Memory operands"):

    RES   the syscall's result, written first
    RDY   nonzero once RES is valid, written second

The stub spins on RDY, copies RES to the accumulator and returns.  The
host clears RDY when the stub has left, and restores the PSW the KCALL
saved at ISP-4 and the ISP itself, which is the part of KRET the stub's
RETURN does not do.

(Until the core read memory operands, an operand outside [SP, MSP) read
as zero and this channel was one bit, PSW.F, with an ACK word; a syscall
could then return only 0 or one generated constant, and the host had to
answer between two adjacent stub instructions, which it could not do
reliably.  docs/plan9_syscalls.md keeps that history.)

The argument and result convention is the 1e libc stub's own:

    write 0x110a:  KCALL $20 ; RETURN R0      (parcels 0005 0802)
    read  0x1102:  KCALL $15 ; RETURN R0      (80F0 0000 000F, 0802)
    open  0x10fa:  KCALL $14 ; RETURN R0      (80F0 0000 000E, 0802)
    close 0x10ee:  KCALL $4  ; RETURN R0      (0001 0802)
    exits 0x12da:  KCALL $8  ; RETURN R0      (0002 0802)
    errstr 0x10f2: KCALL $1  ; RETURN R0      (80F0 0000 0001, 0802)

all in hobbit/bin/cat (the same members are in hobbit/lib/libc.a).  The
arguments are the user's first three stack words above the accumulator:
CSP+4, CSP+8, CSP+12 (R4, R8, R12); the result is returned in the
accumulator CSP+4, which the stub's own `RETURN R0` leaves in place
(offset 0 does not move the SP, PRM p. 3-40).  Cat's call sites are the
witness: `MOV $1,R4; MOVA R32,R8; MOV R28,R12; CALL write` and
`MOV R4,R28` right after the call.

Usage:
    python3 tools/p9shim.py --emit bsv/P9Shim.bsv --file FILE BINARY
    python3 tools/p9shim.py --dump BINARY       (the stub listing)
"""

import argparse
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "asm"))
import hobbit_asm  # noqa: E402  (path must be set first)


# --------------------------------------------------------------------
# The syscall set, as the 1e libc stubs encode it.
# --------------------------------------------------------------------

class Syscall:
    def __init__(self, num, name, symbol, stub, parcels, args, result):
        self.num = num
        self.name = name
        self.symbol = symbol
        self.stub = stub            # address in hobbit/bin/cat
        self.parcels = parcels      # the stub's parcels, address order
        self.args = args            # argument names, in register order
        self.result = result

    def __repr__(self):
        return "Syscall(%d, %s)" % (self.num, self.name)


#: The six syscalls A1 implements.  `stub` and `parcels` are read from
#: hobbit/bin/cat's symbol table and text (tools/p9exec.py reads the
#: file); libc.a's write.z/read.z/open.z/close.z/_exits.z/errstr members
#: are the same code before the link.
SYSCALLS = {
    1: Syscall(1, "errstr", "errstr", 0x10F2,
               (0x80F0, 0x0000, 0x0001, 0x0802),
               ("buf", "n"), "0"),
    4: Syscall(4, "close", "close", 0x10EE,
               (0x0001, 0x0802), ("fd",), "0"),
    8: Syscall(8, "exits", "_exits", 0x12DA,
               (0x0002, 0x0802), ("msg",), "run ends"),
    14: Syscall(14, "open", "open", 0x10FA,
                (0x80F0, 0x0000, 0x000E, 0x0802),
                ("path", "mode"), "fd"),
    15: Syscall(15, "read", "read", 0x1102,
                (0x80F0, 0x0000, 0x000F, 0x0802),
                ("fd", "buf", "n"), "count"),
    20: Syscall(20, "write", "write", 0x110A,
                (0x0005, 0x0802), ("fd", "buf", "n"), "count"),
}

#: Where the definitions live, for the refusal message.
SYSCALL_CITE = ("hobbit/lib/libc.a members write.z, read.z, open.z, "
                "close.z, _exits.z, errstr.z; linked copies at the "
                "symbols above in hobbit/bin/cat")


def syscall_name(num):
    s = SYSCALLS.get(num)
    return s.name if s else "<unknown %d>" % num


def refuse(num):
    raise SystemExit(
        "p9shim: refused syscall %d: not in the 1e syscall table (%s)"
        % (num, SYSCALL_CITE))


# --------------------------------------------------------------------
# The argument convention
# --------------------------------------------------------------------

def arg_addr(sp, k):
    """Address of argument `k` (0-based): the accumulator, then up."""
    return (sp + 4 + 4 * k) & 0xFFFFFFFF


def args_of(sp):
    return tuple(arg_addr(sp, k) for k in range(3))


# --------------------------------------------------------------------
# The host's file table and syscall semantics
# --------------------------------------------------------------------

class Mem:
    """The 32-bit word memory the shim sees (the testbench's array)."""

    def __init__(self, words=None):
        self.words = dict(words or {})

    def read(self, addr):
        return self.words.get(addr & 0xFFFFFFFC, 0)

    def write(self, addr, value):
        self.words[addr & 0xFFFFFFFC] = value & 0xFFFFFFFF

    # Big-endian byte lanes: the byte at a word address is bits 31:24
    # (PRM Figure 1-2, p. 1-4).  This is NOT how 1e runs -- a 1e process
    # has PSW_UL set and its data is little-endian (machine.h:77;
    # tools/p9run.py) -- and `cat` cannot tell: read's bytes go into the
    # words and write's bytes come out of them through the same lanes,
    # and cat itself never looks at one.  The A1 gate therefore says
    # nothing about byte order; tools/p9run.py and tests/test_p9run.py
    # are where the order is pinned (echo, za and zl all depend on it).
    @staticmethod
    def _shift(addr):
        return 8 * (3 - (addr & 3))

    def read_byte(self, addr):
        return (self.read(addr) >> self._shift(addr)) & 0xFF

    def write_bytes(self, addr, data):
        for i, b in enumerate(data):
            a = addr + i
            w = self.read(a)
            self.write(a, (w & ~(0xFF << self._shift(a))) |
                       (b << self._shift(a)))

    def read_bytes(self, addr, n):
        return bytes(self.read_byte(addr + i) for i in range(n))

    def cstring(self, addr, limit=256):
        out = bytearray()
        for i in range(limit):
            b = self.read_byte(addr + i)
            if b == 0:
                break
            out.append(b)
        return bytes(out)


class Shim:
    """The host side of the syscall: a file table over one host file.

    This is the model the testbench implements cycle by cycle; the unit
    tests drive this class directly, so the two cannot quietly disagree
    about what a syscall means.
    """

    def __init__(self, data, name, mem):
        if len(data) > 0xFFFF:
            raise SystemExit("p9shim: file is %d bytes; the generated file "
                             "table is indexed by 16 bits" % len(data))
        self.data = bytes(data)
        self.name = name
        self.mem = mem
        self.offsets = {0: 0}       # stdin is the shim's file
        self.console = bytearray()  # what write(1|2, ...) emitted

    # -- file table ------------------------------------------------
    def fd_open(self, fd):
        return fd in self.offsets

    # -- the dispatch ----------------------------------------------
    def syscall(self, num, sp):
        """Return (result, name) for syscall `num` at SP `sp`.

        The result is the value the stub puts in the accumulator; exits
        has none (the run stops).
        """
        if num not in SYSCALLS:
            refuse(num)
        a = args_of(sp)
        size = len(self.data)
        if num == 1:                              # errstr(buf, n)
            return (0, "errstr")
        if num == 4:                              # close(fd)
            fd = self.mem.read(a[0])
            if fd != 0:
                self.offsets.pop(fd, None)
            return (0, "close")
        if num == 8:                              # exits(msg)
            return (None, "exits")                # the run stops
        if num == 14:                             # open(path, mode)
            self.offsets[FILE_FD] = 0             # the one file, from the top
            return (FILE_FD, "open")
        if num == 15:                             # read(fd, buf, n)
            fd = self.mem.read(a[0])
            buf = self.mem.read(a[1])
            n = self.mem.read(a[2])
            if fd not in self.offsets:
                raise SystemExit(
                    "p9shim: refused read fd=%d: only stdin (0) and the "
                    "shim's file (fd %d, once opened) exist" % (fd, FILE_FD))
            off = self.offsets[fd]
            take = min(n, size - off)
            self.mem.write_bytes(buf, self.data[off:off + take])
            self.offsets[fd] = off + take
            return (take, "read")
        if num == 20:                             # write(fd, buf, n)
            fd = self.mem.read(a[0])
            buf = self.mem.read(a[1])
            n = self.mem.read(a[2])
            if fd not in (1, 2):
                raise SystemExit(
                    "p9shim: refused write fd=%d: only the console (1,2) is "
                    "writable" % fd)
            self.console += self.mem.read_bytes(buf, n)
            return (n, "write")
        refuse(num)


# --------------------------------------------------------------------
# The machine side: the stub, assembled by asm/hobbit_asm.py
# --------------------------------------------------------------------

#: The boot window's free words: the 32-byte Exec header.  Text begins at
#: UTZERO + sizeof(Exec) (0x1020), so 0x1000..0x101f is dead space the
#: loader may use; the 1 Kbyte prefetch window starts at 0x1000, so code
#: placed here is fetchable.
EXEC_HEADER = 0x1000
EXEC_HEADER_BYTES = 32

#: Testbench devices, all outside [SP, MSP): memory words, which the
#: stub reads as absolute operands and the host reads and writes directly.
VB = 0x0C00          # vector page: evmem[VB+0] is the KCALL target
RDY = 0x0C14         # host -> stub: nonzero once RES holds the result
RES = 0x0C18         # host -> stub: the syscall's result
ISP0 = 0x0D00        # interrupt stack top; the event frame at ISP0-16
DB = ISP0 - 12       # the KCALL frame's src word (p. 3-29): the doorbell
FILE_FD = 3          # open's descriptor: the first after 0, 1, 2
SP0 = 0x8000         # user stack top
MSP0 = 0x8100        # 256 bytes above SP: the printed stack cache size
PSW0 = 0x600         # PSW_S|PSW_X: CSP = SP, user level, physical


def stub_source(entry):
    """The stub's assembly.

    `entry` is the image's `_main`.  The stub is the kernel's half of a
    syscall reduced to its machine-visible part: wait until the host has
    done the work, take the result into the accumulator (CSP+4, where
    the 1e libc stubs' callers read it), and return to the libc stub's
    own `RETURN R0`.

    `CMPEQ $0, *$RDY` sets F while RDY is still zero, and `JMPTY` (jump
    if the flag is true, statically predicted taken; the T/F letter is
    the condition and the Y/N letter the prediction) loops on it.  RDY is
    re-read from memory every iteration, so the host may set it at any
    clock.
    """
    jump = (entry - EXEC_HEADER) & 0x3FF
    return """\
; A1 syscall shim, assembled by tools/p9shim.py with asm/hobbit_asm.py.
; Placed at the boot window's Exec header (%(base)#06x); text begins at
; %(text)#06x.
        MOV     $1, R4          ; argc = 1: cat reads its stdin
        JMP     %(jump)#06x     ; _main; the assembler lays the stub out at 0
                                ; and it is placed at 0x1000, so the pcrel
                                ; literal is (entry - 0x1000)
p9stub: CMPEQ   $0, *$%(rdy)#06x   ; 1) wait: F = 1 while RDY is zero
        JMPTY   p9stub
        MOV     *$%(res)#06x, R4   ; 2) the result, into the accumulator
        RETURN  R0              ; 3) back to the libc stub
""" % {"base": EXEC_HEADER, "text": 0x1020, "jump": jump, "rdy": RDY,
       "res": RES}


def build_stub(entry):
    """Assemble the stub; return (words, symbols, listing text)."""
    src = stub_source(entry)
    listing, parcels, _addresses = hobbit_asm.listing_from_assembly(
        src, "<p9shim>", False)
    items = hobbit_asm.parse_source(src, "<p9shim>")
    symbols, _total = hobbit_asm.layout(items)
    parcel_count = len(parcels)
    if parcel_count * 2 > EXEC_HEADER_BYTES:
        raise SystemExit(
            "p9shim: the stub is %d parcels (%d bytes) but the Exec header "
            "holds %d bytes" % (parcel_count, parcel_count * 2,
                                EXEC_HEADER_BYTES))
    padded, _ = hobbit_asm.pad_parcels(list(parcels))
    words = hobbit_asm.parcels_to_words(padded)
    addr = {k: EXEC_HEADER + v for k, v in symbols.items()
            if k.startswith("p9")}
    return words, addr, listing


# --------------------------------------------------------------------
# The generated Bluespec package
# --------------------------------------------------------------------

def emit_bsv(path, words, addr, file_data, file_name):
    out = []
    w = out.append
    w("// Generated by tools/p9shim.py --emit; do not edit.")
    w("// The A1 syscall shim: the stub at the boot window's Exec header,")
    w("// the testbench's device addresses, and the host file to serve.")
    w("package P9Shim;")
    w("")
    w("import HobbitTypes::*;")
    w("")
    w("function Word shimBase();     return 32'h%08x; endfunction" % EXEC_HEADER)
    w("function Word shimBoot();     return 32'h%08x; endfunction" % EXEC_HEADER)
    w("function Word shimStub();     return 32'h%08x; endfunction"
      % addr["p9stub"])
    w("function Word shimVb();       return 32'h%08x; endfunction" % VB)
    w("function Word shimDb();       return 32'h%08x; endfunction" % DB)
    w("function Word shimRdy();      return 32'h%08x; endfunction" % RDY)
    w("function Word shimRes();      return 32'h%08x; endfunction" % RES)
    w("function Word shimFileFd();   return 32'd%d; endfunction" % FILE_FD)
    w("function Word shimIsp0();     return 32'h%08x; endfunction" % ISP0)
    w("function Word shimSp0();      return 32'h%08x; endfunction" % SP0)
    w("function Word shimMsp0();     return 32'h%08x; endfunction" % MSP0)
    w("function Word shimPsw0();     return 32'h%08x; endfunction" % PSW0)
    w("")
    w("function Word shimCodeLength(); return 32'd%d; endfunction" % len(words))
    w("function Word shimCodeWord(Bit#(16) i);")
    w("  case (i)")
    for i, x in enumerate(words):
        w("    %d: return 32'h%08x;" % (i, x))
    w("    default: return 32'h0;")
    w("  endcase")
    w("endfunction")
    w("")
    w("function Bit#(32) shimFileLength(); return 32'd%d; endfunction"
      % len(file_data))
    w("function Bit#(8) shimFileByte(Bit#(16) i);")
    w("  case (i)")
    for i, b in enumerate(file_data):
        w("    %d: return 8'h%02x;" % (i, b))
    w("    default: return 8'h00;")
    w("  endcase")
    w("endfunction")
    nb = file_name.encode()
    w("")
    w("function Bit#(32) shimNameLength(); return 32'd%d; endfunction" % len(nb))
    w("function Bit#(8) shimNameByte(Bit#(8) i);")
    w("  case (i)")
    for i, b in enumerate(nb):
        w("    %d: return 8'h%02x;" % (i, b))
    w("    default: return 8'h00;")
    w("  endcase")
    w("endfunction")
    w("")
    w("endpackage")
    pathlib.Path(path).write_text("\n".join(out) + "\n", encoding="ascii")


def check_window(entry):
    """The stub needs the Exec header inside the boot window."""
    base = entry & ~0x3FF
    if base != EXEC_HEADER:
        raise SystemExit(
            "p9shim: entry 0x%04x has boot window base 0x%04x, not 0x%04x; "
            "the stub must live in the Exec header, so only binaries whose "
            "entry is in 0x1000..0x13ff (cat) can be shimmed" %
            (entry, base, EXEC_HEADER))
    return base


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("binary")
    ap.add_argument("--file", help="the host file the shim serves")
    ap.add_argument("--emit", metavar="BSV", help="write the P9Shim package")
    ap.add_argument("--dump", action="store_true", help="print the stub")
    ap.add_argument("--entry", type=lambda s: int(s, 0),
                    help="override the binary's entry (for tests)")
    args = ap.parse_args(argv)

    sys.path.insert(0, str(HERE))
    import p9exec
    exe = p9exec.read(args.binary)
    entry = args.entry if args.entry is not None else exe["entry"]
    check_window(entry)

    data = b""
    name = args.file or ""
    if args.file:
        data = pathlib.Path(args.file).read_bytes()
    words, addr, listing = build_stub(entry)
    if args.dump:
        print(listing)
        for k in sorted(addr):
            print("  %-8s 0x%04x" % (k, addr[k]))
    if args.emit:
        emit_bsv(args.emit, words, addr, data, name)
        print("p9shim: wrote %s: %d words of stub, file %s (%d bytes)"
              % (args.emit, len(words), name, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
