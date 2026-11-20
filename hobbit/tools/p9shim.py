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
it, does the syscall, and clears it.  The stub cannot read that word --
its operands are the stack cache -- and it does not need to: the host
knows the id from the frame.

Why the stub does not ring a doorbell of its own (a model fact, not a
choice): an operand read outside [SP, MSP) returns zero in this model
(`docs/isa_inventory.md` section 1.6, "the box's defined miss"), so a
stub running with the interrupt stack as CSP cannot read *any* memory
word, the event frame included.  The hardware's own frame write is
therefore the ring: it carries the id, it is in memory, and the host
clears it exactly as the boot plan's doorbell is cleared.  Host -> stub
is a single bit, PSW.F: the stub spins on it (`JMPFN wait`) and the host
raises it to release.  The stub then dispatches with a second `KCALL $0`
through the vector page, which the host has pointed at the result
handler for this syscall -- the only host-writable readable location in
the model (the testbench's vector page `evmem`).

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

    def read_byte(self, addr):
        return (self.read(addr) >> (8 * (addr & 3))) & 0xFF

    def write_bytes(self, addr, data):
        for i, b in enumerate(data):
            a = addr + i
            w = self.read(a)
            self.write(a, (w & ~(0xFF << (8 * (a & 3)))) |
                       (b << (8 * (a & 3))))

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


class Kind:
    """Which of the stub's two result paths a syscall takes."""
    ZERO = 0     # MOV $0,R4  (close, errstr, EOF)
    SIZE = 1     # MOV $S,R4  (open's fd, the bytes moved)


class Shim:
    """The host side of the syscall: a file table over one host file.

    This is the model the testbench implements cycle by cycle; the unit
    tests drive this class directly, so the two cannot quietly disagree
    about what a syscall means.
    """

    def __init__(self, data, name, mem):
        if len(data) > 0xFFFF:
            raise SystemExit("p9shim: file is %d bytes; the stub's only "
                             "immediate is 16 bits" % len(data))
        self.data = bytes(data)
        self.name = name
        self.mem = mem
        self.open_fd = 3            # the first fd after 0,1,2
        self.offsets = {0: 0}       # stdin is the shim's file
        self.console = bytearray()  # what write(1|2, ...) emitted

    # -- file table ------------------------------------------------
    def fd_open(self, fd):
        return fd in self.offsets

    # -- the dispatch ----------------------------------------------
    def syscall(self, num, sp):
        """Return (result, kind) for syscall `num` at SP `sp`.

        `kind` names the stub's path: Kind.ZERO returns 0, Kind.SIZE
        returns the file's length.  A result that is neither cannot be
        delivered by this machine's one-bit channel and is refused.
        """
        if num not in SYSCALLS:
            refuse(num)
        a = args_of(sp)
        size = len(self.data)
        if num == 1:                              # errstr(buf, n)
            return (0, Kind.ZERO, "errstr")
        if num == 4:                              # close(fd)
            fd = self.mem.read(a[0])
            self.offsets.pop(fd, None)
            return (0, Kind.ZERO, "close")
        if num == 8:                              # exits(msg)
            return (None, None, "exits")          # the run stops
        if num == 14:                             # open(path, mode)
            if size == 0:
                raise SystemExit(
                    "p9shim: refused open: the shim's one file is empty and "
                    "the machine side cannot return an fd")
            self.offsets[size] = 0                # the fd is the file length
            return (size, Kind.SIZE, "open")
        if num == 15:                             # read(fd, buf, n)
            fd = self.mem.read(a[0])
            buf = self.mem.read(a[1])
            n = self.mem.read(a[2])
            if fd not in (0, size):
                raise SystemExit(
                    "p9shim: refused read fd=%d: only 0 and the shim's file "
                    "(fd %d) exist" % (fd, size))
            off = self.offsets[fd]
            take = min(n, size - off)
            if take not in (0, size):
                raise SystemExit(
                    "p9shim: refused read of %d bytes: the machine's result "
                    "channel can name only 0 and %d" % (take, size))
            self.mem.write_bytes(buf, self.data[off:off + take])
            self.offsets[fd] = off + take
            return (take, Kind.SIZE if take else Kind.ZERO, "read")
        if num == 20:                             # write(fd, buf, n)
            fd = self.mem.read(a[0])
            buf = self.mem.read(a[1])
            n = self.mem.read(a[2])
            if fd not in (1, 2):
                raise SystemExit(
                    "p9shim: refused write fd=%d: only the console (1,2) is "
                    "writable" % fd)
            if n != size:
                raise SystemExit(
                    "p9shim: refused write of %d bytes: the machine's result "
                    "channel can name only 0 and %d" % (n, size))
            self.console += self.mem.read_bytes(buf, n)
            return (n, Kind.SIZE, "write")
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

#: Testbench devices, all outside [SP, MSP) so that the model's operand
#: path (the stack cache) never sees them.
VB = 0x0C00          # vector page: evmem[VB+0] is the KCALL target
DB = 0x0C10          # the KCALL frame's src word: the doorbell
ACK = 0x0C14         # the stub's handshake word (1 = released, 2 = armed)
ISP0 = 0x0D00        # interrupt stack top; the event frame at ISP0-16
SP0 = 0x8000         # user stack top
MSP0 = 0x8100        # 256 bytes above SP: the printed stack cache size
PSW0 = 0x600         # PSW_S|PSW_X: CSP = SP, user level, physical


def stub_source(entry, size, label=""):
    """The stub's assembly.

    `entry` is the image's `_main`; `size` is the number of bytes the
    shim transfers, carried as a 16-bit immediate because the host cannot
    put a data value into the machine (see the module comment).

    The result channel is PSW.F plus one ACK word in memory (the shim's
    device page), which is the only host-writable bit and the only
    machine-writable word the host can read:

        host: F=1 (release)        -> stub: ACK 1
        host: ACK 1 seen, F=0      -> stub: ACK 2 (armed)
        host: ACK 2 seen, F=value  -> stub: 0 or `size`, RETURN R0

    So a syscall can return exactly two values: 0 and the generated
    size.  That is narrow, and docs/plan9_syscalls.md records why: the
    model reads no operand outside [SP, MSP), has no KRET and no
    CPU-register instructions, and -- a model limit this shim found -- a
    KCALL executed *inside* the stub deadlocks the pipeline, so the
    vector page cannot be used as a second dispatch.
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
p9stub: JMPFN   p9stub          ; 1) wait for the host's release (PSW.F = 1)
        MOV     $1, *$%(ack)#06x   ; 2) ACK 1: released
p9armed:JMPFY   p9armed         ; 3) wait for the host to clear F (armed)
        MOV     $2, *$%(ack)#06x   ; 4) ACK 2: sampling the value bit now
        MOV     $0, R4          ; default result: zero
        JMPFN   p9ret           ; 5) F = 0 -> zero
        MOV     $%(size)d, R4   ;    F = 1 -> the bytes this shim moved
p9ret:  RETURN  R0
""" % {"base": EXEC_HEADER, "text": 0x1020, "jump": jump, "ack": ACK,
       "size": size}


def build_stub(entry, size):
    """Assemble the stub; return (words, symbols, listing text)."""
    src = stub_source(entry, size)
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

def emit_bsv(path, words, addr, size, file_data, file_name):
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
    for name, fn in (("p9stub", "shimStub"), ("p9armed", "shimArmed"),
                     ("p9ret", "shimRet")):
        w("function Word %s(); return 32'h%08x; endfunction"
          % (fn, addr[name]))
    w("function Word shimVb();       return 32'h%08x; endfunction" % VB)
    w("function Word shimDb();       return 32'h%08x; endfunction" % DB)
    w("function Word shimAck();      return 32'h%08x; endfunction" % ACK)
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
    words, addr, listing = build_stub(entry, len(data))
    if args.dump:
        print(listing)
        for k in sorted(addr):
            print("  %-8s 0x%04x" % (k, addr[k]))
    if args.emit:
        emit_bsv(args.emit, words, addr, len(data), data, name)
        print("p9shim: wrote %s: %d words of stub, file %s (%d bytes)"
              % (args.emit, len(words), name, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
