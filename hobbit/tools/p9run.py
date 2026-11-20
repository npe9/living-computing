#!/usr/bin/env python3
"""Run a 1st Edition Plan 9 Hobbit binary on the reference model.

`sem/hobbit_sem.py` executes the instructions; this file is the kernel's
side of the process: the exec frame, the system calls and a file tree.
It is the *oracle* for the Bluespec runs of the same binaries
(bsv/run_p9.sh): it says which instructions and system calls a program
needs, how many instructions it retires, and what it writes.

Everything the kernel does here is taken from the release, not guessed:

  exec frame     sys/src/9/port/sysproc.c sysexec() and
                 sys/src/9/hobbit/trap.c execregs():
                     ssize = 4*(nargs+1) + roundup(nbytes, 4)
                     if((ssize+4) & 7) ssize += 4
                     argv[] at USTKTOP-ssize, the strings at USTKTOP-nbytes
                     sp = USTKTOP - QUADALIGN(ssize + 12)
                     sp[0] = USTKTOP-4; sp[2] = USTKTOP-ssize
                     msp = USTKTOP; pc = entry; return nargs
                 The returned nargs is the accumulator, sp[1] (CSP+4),
                 which is `argc+0(FP)` in libc's main9.s; sp[2] is
                 `argv+4(FP)`.
  USTKTOP        sys/src/9/hobbit/mem.h: KZERO = KTEXTBASE = RAMBASE =
                 0x80000000 (the `ram` kernel)
  syscall ids    sys/src/libc/9syscall/sys.h
  syscall ABI    the id is KCALL's source (PRM p. 3-29); the arguments
                 are the caller's CSP+4, +8, +12, +16 and the result is
                 the accumulator CSP+4 (the libc stubs: `KCALL $n;
                 RETURN R0`)
  byte order     1e runs the Hobbit little-endian: l.s sets CONFIG.KL
                 and a process's PSW carries PSW_UL
                 (sys/src/9/hobbit/machine.h:24,77; raml.s builds the
                 first CRET's PSW as PSW_VP|PSW_UL|PSW_S).  A file's bytes
                 are therefore the memory's bytes with BYTE0 in bits 7:0
                 (PRM Figure 1-3, p. 1-4), text and data alike; the text
                 is still *fetched* big-endian (p. 1-4 note), which is why
                 zl writes each text word byte-reversed.
  addressing     physical.  The real process runs with PSW_VP; this
                 runner maps nothing and uses the addresses as they are.

The model executes KCALL itself (the event frame at ISP-12/-8/-4).  This
file then plays the kernel: it reads the id from the frame, does the
call against the host tree, puts the result in the accumulator and does
KRET's part (PC and PSW from the frame, ISP += 16).

Stack cache: both this run and the Bluespec run start with the cache
empty (MSP = SP) and empty it again at every kernel entry, where the
real kernel would have it loaded; see `run` and the stub notes below.

`--hri FILE` writes the retirement trace and `--record FILE` writes the
recording that bsv/P9HostTb.bsv replays (boot memory, start state, every
kernel entry); the format is in bsv/p9host.c.

Files: paths are resolved inside --root (the process's `/` and its
working directory); a path that would leave it is refused.

    python3 tools/p9run.py --root DIR hobbit/tools/plan9-1e/hobbit/bin/za file.s
"""

import argparse
import collections
import os
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sem"))
sys.path.insert(0, str(HERE.parent / "asm"))
import p9exec          # noqa: E402
import hobbit_sem      # noqa: E402

USTKTOP = 0x80000000
USTKSIZE = 4 * 1024 * 1024  # mem.h: size of the user stack

# The kernel's page.  Page 0 is below UTZERO (0x1000) and no 1e process
# maps it, so the vector table, the interrupt stack, the stubs and their
# device words go there; every address fits a 16-bit absolute operand.
VB0 = 0x0C00                # vector base: +0 KCALL (p. 3-29), +12 unimp (p. 1-39)
RDY = 0x0C14                # host -> stub: nonzero when the entry is served
RES = 0x0C18                # host -> stub: the result / the resume PC
GO = 0x0C1C                 # stub -> host: 1 system call, 2 floating point
FLAG = 0x0C20               # host -> stub: the PSW.F to leave
TMP = 0x0C24                # stub scratch: the SP, for ENTER's flush
STUB = 0x0C40               # the two stubs' code
ISP0 = 0x0D00               # interrupt stack top; KCALL's frame is ISP0-16..
KPAGE = (0x0C00, 0x0E00)
PSW_USER = 0x8600           # PSW_UL | PSW_X | PSW_S: little-endian user, CSP = SP

SYSCALLS = {
    0: "sysr1", 1: "errstr", 2: "bind", 3: "chdir", 4: "close", 5: "dup",
    6: "alarm", 7: "exec", 8: "exits", 11: "fstat", 12: "segbrk",
    13: "mount", 14: "open", 15: "read", 16: "seek", 17: "sleep",
    18: "stat", 19: "rfork", 20: "write", 21: "pipe", 22: "create",
    24: "brk_", 25: "remove", 26: "wstat", 27: "fwstat", 28: "notify",
    29: "noted", 30: "segattach", 31: "segdetach", 32: "segfree",
    33: "segflush", 34: "rendezvous", 35: "unmount", 36: "wait",
}


class Stop(Exception):
    pass


# --------------------------------------------------------------------
# The machine side of a kernel entry, for the Bluespec run
# --------------------------------------------------------------------
#
# On the reference model the kernel's work is done between two steps.  On
# the Bluespec core something has to occupy the machine meanwhile, and
# the host cannot see inside the stack cache.  These two stubs are that
# something; `p9run` never executes them (bsv/P9HostTb.bsv does), but it
# lays them out, because the recording it writes is the Bluespec run's
# whole boot image.
#
#   MOVA R0, *$TMP ; ENTER *$TMP
#       The printed ENTER with a source that is not a stack offset
#       "flush[es] stack cache unconditionally" and sets MSP = SP = the
#       target (p. 3-19); the absolute form fetches the target from
#       memory (p. 3-20, case 4), and MOVA has just stored the SP there.
#       So SP is unchanged, the cache is empty, and every word of the
#       user's stack is in memory, where the host can read the arguments
#       and the buffers.  The reference run applies the same policy:
#       MSP = SP at exec and after every kernel entry (`run`).
#   MOV $n, *$GO
#       rings the host.
#   CMPEQ $0, *$RDY ; JMPTY ...
#       waits; RDY is re-read from memory every time round.
#   MOV *$RES, R4            (system call only) the result
#   CMPEQ $1, *$FLAG
#       leaves PSW.F as the host asks: the flag the process had before a
#       system call, or the flag a floating-point compare produced.
#   JMP **$addr
#       back to the process: the PC KCALL saved at ISP-8 (p. 3-29), or
#       the PC after the emulated instructions, which the host put in RES.
#
# What the host does through the testbench instead of the machine doing
# it: KRET's PSW and ISP.  The model has no KRET.

def stub_source():
    return """\
ksys:   MOVA    R0, *$%(tmp)#06x
        ENTER   *$%(tmp)#06x
        MOV     $1, *$%(go)#06x
kwait:  CMPEQ   $0, *$%(rdy)#06x
        JMPTY   kwait
        MOV     $0, *$%(rdy)#06x
        MOV     *$%(res)#06x, R4
        CMPEQ   $1, *$%(flag)#06x
        JMP     **$%(retpc)#06x
kfp:    MOVA    R0, *$%(tmp)#06x
        ENTER   *$%(tmp)#06x
        MOV     $2, *$%(go)#06x
fwait:  CMPEQ   $0, *$%(rdy)#06x
        JMPTY   fwait
        MOV     $0, *$%(rdy)#06x
        CMPEQ   $1, *$%(flag)#06x
        JMP     **$%(res)#06x
""" % {"tmp": TMP, "go": GO, "rdy": RDY, "res": RES, "flag": FLAG,
       "retpc": ISP0 - 8}


def build_stubs():
    """Assemble the stubs; return ({address: word}, {label: address})."""
    import hobbit_asm
    src = stub_source()
    _listing, parcels, _addresses = hobbit_asm.listing_from_assembly(
        src, "<p9run stub>", False)
    symbols, _total = hobbit_asm.layout(hobbit_asm.parse_source(
        src, "<p9run stub>"))
    padded, _ = hobbit_asm.pad_parcels(list(parcels))
    words = hobbit_asm.parcels_to_words(padded)
    image = {STUB + 4 * i: w for i, w in enumerate(words)}
    labels = {k: STUB + v for k, v in symbols.items()}
    if STUB + 4 * len(words) > ISP0 - 64:
        raise SystemExit("p9run: the stubs run into the interrupt stack")
    image[VB0 + 0] = labels["ksys"]
    image[VB0 + 12] = labels["kfp"]
    return image, labels


#: arguments each system call reads (the Bluespec run compares that many)
NARGS = {"exits": 1, "errstr": 1, "brk_": 1, "open": 2, "create": 3,
         "close": 1, "read": 3, "write": 3, "seek": 3, "remove": 1}


class Recorder:
    """The recording bsv/p9host.c replays (format: that file's header)."""

    def __init__(self):
        self.events = []
        self.cur = None

    def begin(self, kind, ident, nargs, args):
        self.cur = ["E %s %x %x %s" % (kind, ident, nargs,
                                       " ".join("%x" % a for a in args))]

    def store(self, addr, data):
        if self.cur is not None and data:
            self.cur.append("B %x %s" % (addr, bytes(data).hex()))

    def output(self, name, offset, addr, n):
        if self.cur is not None:
            self.cur.append("O %s %x %x %x" % (name, offset, addr, n))

    def end(self, result, flag, done):
        self.cur.append("R %x %x %x" % (result & 0xFFFFFFFF, flag, done))
        self.events.append(self.cur)
        self.cur = None

    def write(self, path, memory, start, ranges):
        with open(path, "w") as f:
            for lo, hi in ranges:
                f.write("L %x %x\n" % (lo, hi))
            for addr in sorted(memory):
                if memory[addr]:
                    f.write("M %x %x\n" % (addr, memory[addr]))
            f.write("S %x %x %x %x %x\n" % start)
            f.write("G %x %x %x %x\n" % (GO, RDY, RES, FLAG))
            for ev in self.events:
                f.write("\n".join(ev) + "\n")


class Machine:
    """Byte access to the reference model's word memory (little-endian)."""

    def __init__(self, state):
        self.state = state
        self.rec = None         # a Recorder, while the kernel is storing

    def word(self, addr):
        return self.state.memory.get(addr & 0xFFFFFFFC, 0)

    def set_word(self, addr, value):
        self.state.memory[addr & 0xFFFFFFFC] = value & 0xFFFFFFFF

    def byte(self, addr):
        return (self.word(addr) >> (8 * (addr & 3))) & 0xFF

    def set_bytes(self, addr, data):
        if self.rec is not None:
            self.rec.store(addr, data)
        self._set_bytes(addr, data)

    def kernel_word(self, addr, value):
        """A word the kernel stores (recorded as its four bytes)."""
        self.set_bytes(addr, (value & 0xFFFFFFFF).to_bytes(4, "little"))

    def _set_bytes(self, addr, data):
        for i, b in enumerate(data):
            a = (addr + i) & 0xFFFFFFFF
            sh = 8 * (a & 3)
            self.set_word(a, (self.word(a) & ~(0xFF << sh)) | (b << sh))

    def bytes(self, addr, n):
        return bytes(self.byte(addr + i) for i in range(n))

    def cstring(self, addr, limit=4096):
        out = bytearray()
        for i in range(limit):
            b = self.byte(addr + i)
            if b == 0:
                return bytes(out)
            out.append(b)
        raise Stop("p9run: unterminated string at 0x%08x" % addr)


def load(exe, state):
    """Map text and data (the file's bytes); bss reads as zero."""
    m = Machine(state)
    syms = p9exec.symbols(exe)
    n = exe["text"] // 4
    for k, w in enumerate(p9exec._words(exe, exe["text_off"], n)):
        state.memory[p9exec.TEXTBASE + 4 * k] = w
    bdata = syms["bdata"][0]
    blob = exe["blob"][exe["data_off"]:exe["data_off"] + exe["data"]]
    m.set_bytes(bdata, blob)
    return bdata + exe["data"] + exe["bss"]


def exec_frame(state, argv):
    """sysexec()/execregs(): returns (sp, msp)."""
    m = Machine(state)
    strings = [a.encode("latin-1") + b"\0" for a in argv]
    nargs = len(strings)
    nbytes = sum(len(s) for s in strings)
    ssize = 4 * (nargs + 1) + ((nbytes + 3) & ~3)
    if (ssize + 4) & 7:
        ssize += 4
    vec = USTKTOP - ssize
    charp = USTKTOP - nbytes
    for i, s in enumerate(strings):
        m.set_word(vec + 4 * i, charp)
        m.set_bytes(charp, s)
        charp += len(s)
    m.set_word(vec + 4 * nargs, 0)
    sp = USTKTOP - ((ssize + 12 + 15) & ~15)
    m.set_word(sp + 0, USTKTOP - 4)
    m.set_word(sp + 4, nargs)           # execregs' return value: R4
    m.set_word(sp + 8, vec)
    return sp, USTKTOP


class Kernel:
    def __init__(self, root, machine, bss_end, console):
        self.root = os.path.realpath(root)
        self.m = machine
        self.brk = bss_end
        self.console = console
        self.fds = {0: None, 1: "console", 2: "console"}
        self.max_brk = bss_end
        self.errstr = b""
        self.trace = []
        self.fp_traps = []      # (pc, [mnemonics]) per handler entry
        self.exit_msg = None

    def host_path(self, name):
        p = os.path.realpath(os.path.join(self.root, name.lstrip("/")))
        if p != self.root and not p.startswith(self.root + os.sep):
            raise Stop("p9run: refused path %r: outside --root" % name)
        return p

    def new_fd(self, f):
        fd = 0
        while fd in self.fds:
            fd += 1
        self.fds[fd] = f
        return fd

    def fail(self, msg):
        self.errstr = msg.encode()
        return 0xFFFFFFFF

    def call(self, num, sp):
        m = self.m
        a = [m.word(sp + 4 + 4 * k) for k in range(4)]
        name = SYSCALLS.get(num)
        if name == "exits":
            self.exit_msg = m.cstring(a[0]).decode("latin-1") if a[0] else ""
            return None
        if name == "errstr":
            m.set_bytes(a[0], (self.errstr + b"\0" * 64)[:64])
            return 0
        if name == "brk_":
            self.brk = a[0]
            self.max_brk = max(self.max_brk, a[0])
            return 0
        if name == "open":
            path = m.cstring(a[0]).decode("latin-1")
            mode = a[1] & 3
            try:
                f = open(self.host_path(path), {0: "rb", 1: "r+b", 2: "r+b"}[mode])
            except OSError as e:
                return self.fail("%s: %s" % (path, e.strerror))
            return self.new_fd(f)
        if name == "create":
            path = m.cstring(a[0]).decode("latin-1")
            try:
                f = open(self.host_path(path), "w+b")
            except OSError as e:
                return self.fail("%s: %s" % (path, e.strerror))
            return self.new_fd(f)
        if name == "close":
            f = self.fds.pop(a[0], None)
            if f not in (None, "console"):
                f.close()
            return 0
        if name == "read":
            f = self.fds.get(a[0], "absent")
            if f == "absent" or f == "console":
                return self.fail("fd %d not open for reading" % a[0])
            data = b"" if f is None else f.read(a[2])
            m.set_bytes(a[1], data)
            return len(data)
        if name == "write":
            f = self.fds.get(a[0], "absent")
            if f == "absent" or f is None:
                return self.fail("fd %d not open for writing" % a[0])
            data = m.bytes(a[1], a[2])
            if f == "console":
                if m.rec is not None:
                    m.rec.output("-", 0, a[1], a[2])
                self.console.write(data)
            else:
                if m.rec is not None:
                    m.rec.output(os.path.relpath(f.name, self.root),
                                 f.tell(), a[1], a[2])
                f.write(data)
            return len(data)
        if name == "seek":
            f = self.fds.get(a[0], "absent")
            if f in ("absent", None, "console"):
                return self.fail("fd %d cannot seek" % a[0])
            off = a[1] - (1 << 32) if a[1] & 0x80000000 else a[1]
            f.seek(off, a[2])
            return f.tell()
        if name == "remove":
            path = m.cstring(a[0]).decode("latin-1")
            try:
                os.remove(self.host_path(path))
            except OSError as e:
                return self.fail("%s: %s" % (path, e.strerror))
            return 0
        raise Stop("p9run: refused syscall %d (%s) args %s"
                   % (num, name, " ".join("%08x" % x for x in a)))


# --------------------------------------------------------------------
# Floating point: the unimplemented-instruction handler
# --------------------------------------------------------------------
#
# The ATT92010 has no floating point: Table 1-18/1-20 print those opcodes
# as "unimp", and an attempt to execute one performs the unimplemented
# instruction sequence (PRM p. 1-39): *(CSP) = PC of the opcode,
# PC = *(VB+12).  1e's handler is sys/src/9/hobbit/fprt0.s + fpihobbit.c
# (+ fpi.c), user-level code that decodes the instruction itself,
# emulates it, and goes on emulating while the next instruction is also
# floating point.  That handler is not available as a Hobbit binary (it
# is C, and the release ships no zc), so this is a transcription of
# fpihobbit.c's decode -- opcodes, operand modes, operand order, the
# `sequence` strings -- with the arithmetic done in host IEEE doubles
# instead of fpi.c's 53+3-bit `Internal`.  Moves, compares and integer
# conversions are exact; FADD/FSUB/FMUL/FDIV round as the host does.

FP_OPS = {            # fpihobbit.c getopcode(): code -> (name, sequence)
    17: ("FMOV", "0f2"), 25: ("FCMPGT", "01f"), 26: ("FCMPEQ", "01f"),
    40: ("FSUB", "01f2"), 41: ("FMUL", "01f2"), 42: ("FDIV", "01f2"),
    43: ("FADD", "01f2"), 56: ("FSUB3", "01f3"), 57: ("FMUL3", "01f3"),
    58: ("FDIV3", "01f3"), 59: ("FADD3", "01f3"),
}
FP_MODES = {          # fpihobbit.c getopmode(): mode -> (address, type)
    0: ("abs", "F"), 1: ("abs", "D"), 4: ("stk", "F"), 5: ("stk", "D"),
    8: ("ind", "F"), 9: ("ind", "D"), 12: ("abs", "W"), 13: ("stk", "W"),
    14: ("ind", "W"), 15: ("imm", "I"),
}


def _parcel(m, pc):
    w = m.word(pc)
    return (w & 0xFFFF) if (pc & 3) else (w >> 16)


def _fp_get(m, typ, v):
    if typ == "I":                      # the immediate is single bits
        return struct.unpack(">f", struct.pack(">I", v))[0]
    if typ == "F":
        return struct.unpack(">f", struct.pack(">I", m.word(v)))[0]
    if typ == "D":                      # fpi.h Double: l at +0, h at +4
        return struct.unpack(">d", struct.pack(">II", m.word(v + 4),
                                               m.word(v)))[0]
    w = m.word(v)
    return float(w - (1 << 32) if w & 0x80000000 else w)


def _fp_put(m, typ, v, x):
    if typ == "F":
        try:
            bits = struct.unpack(">I", struct.pack(">f", x))[0]
        except OverflowError:
            bits = 0x7F800000 | (0x80000000 if x < 0 else 0)
        m.kernel_word(v, bits)
    elif typ == "D":
        h, lo = struct.unpack(">II", struct.pack(">d", x))
        m.kernel_word(v, lo)
        m.kernel_word(v + 4, h)
    elif typ == "W":                    # fpii2w: truncate, saturate
        mag = min(int(abs(x)), 0x7FFFFFFF) if x == x else 0
        m.kernel_word(v, -mag if x < 0 else mag)
    else:
        raise Stop("p9run: fpi: store to an immediate")


def fpi(m, state):
    """fpihobbit.c fpi(): emulate the run of FP instructions at state.pc.

    Returns the mnemonics emulated ([] when the opcode at PC is not one
    of fpi's).
    """
    done = []
    while True:
        pc = state.pc & ~1
        p = _parcel(m, pc)
        if not (p & 0x8000) or ((p >> 8) & 0x3F) not in FP_OPS:
            return done
        name, sequence = FP_OPS[(p >> 8) & 0x3F]
        long_form = bool(p & 0x4000)
        pc += 2
        vals = []
        for mode in ((p >> 4) & 0xF, p & 0xF):
            if mode not in FP_MODES:
                raise Stop("p9run: fpi: operand mode %d at 0x%08x"
                           % (mode, state.pc))
            kind, typ = FP_MODES[mode]
            field = _parcel(m, pc)
            pc += 2
            if long_form or kind == "imm":
                field = (field << 16) | _parcel(m, pc)
                pc += 2
            if kind == "abs" and not long_form:
                field |= pc & 0xE0000000
            if kind in ("stk", "ind"):
                field = (state.sp + field) & 0xFFFFFFFF
            if kind == "ind":
                field = m.word(field)
            vals.append((typ, field))
        (lt, lv), (rt, rv) = vals
        left = right = result = None
        for step in sequence:
            if step == "0":
                left = _fp_get(m, lt, lv)
            elif step == "1":
                right = _fp_get(m, rt, rv)
            elif step == "f":
                if name == "FMOV":
                    result = left
                elif name in ("FCMPGT", "FCMPEQ"):
                    flag = (left > right) if name == "FCMPGT" else (left == right)
                    state.psw = (state.psw | 0x10) if flag else (state.psw & ~0x10)
                elif name.startswith("FSUB"):
                    result = right - left
                elif name.startswith("FMUL"):
                    result = left * right
                elif name.startswith("FADD"):
                    result = left + right
                else:                               # fpidiv: y/x = right/left
                    try:
                        result = right / left
                    except ZeroDivisionError:
                        result = float("nan") if right == 0 or right != right \
                            else float("inf") * (1 if right > 0 else -1)
            elif step == "2":
                _fp_put(m, rt, rv, result)
            elif step == "3":
                _fp_put(m, rt, (state.sp + 4) & 0xFFFFFFFF, result)
        state.pc = pc
        done.append(name)


def kernel_entry_flush(state):
    """The stub's `MOVA R0, *$TMP ; ENTER *$TMP` (see `stub_source`): the
    whole window goes to memory and the cache is left empty, MSP = SP."""
    hobbit_sem.cache_flush(state, None, state.msp,
                           (state.msp - state.sp) // 16)
    state.msp = state.sp


def mnemonic_key(parcels):
    p0 = parcels[0]
    if p0 & 0x8000 == 0:
        return "1p op%02x" % ((p0 >> 10) & 0x1F)
    n = 3 if (p0 & 0xC000) == 0x8000 else 5
    return "%dp op%02x sm%x dm%x" % (n, (p0 >> 8) & 0x3F, (p0 >> 4) & 0xF,
                                     p0 & 0xF)


def run(binary, argv, root, max_steps, console, census=False, verbose=False,
        record=None, hri=None):
    """Run `binary`; optionally write the Bluespec run's recording and
    the HRI trace (one line per retirement, the comparison's reference).
    """
    exe = p9exec.read(binary)
    state = hobbit_sem.State(pc=exe["entry"], psw=PSW_USER, isp=ISP0, vb=VB0,
                             config_kl=True)    # l.s sets CONFIG.KL
    bss_end = load(exe, state)
    state.sp, _ustktop = exec_frame(state, argv)
    # execregs sets msp = USTKTOP (with a "???" of its own); the cache is
    # then loaded by the kernel's return.  Neither model has that return,
    # and the Bluespec core's cache cannot be loaded from memory, so both
    # runs start with the cache empty, MSP = SP: every stack word is in
    # memory, which is also the state after each kernel entry (the stub's
    # ENTER flush).  CATCH and ENTER then fill it as the program runs.
    state.msp = state.sp
    # The cache's contents are modelled (hobbit_sem.State.cache): za reads
    # a stack word it never wrote, and what it gets is what the cache slot
    # held, which only a model of the array can say.
    state.cache = [0] * 64
    stubs, _labels = build_stubs()
    state.memory.update(stubs)
    m = Machine(state)
    k = Kernel(root, m, bss_end, console)
    recorder = Recorder() if record else None
    boot_memory = dict(state.memory) if record else None
    start = (state.pc, state.sp, state.psw, state.isp, state.vb)
    hri_file = open(hri, "w") if hri else None
    ops = collections.Counter()
    steps = 0
    status = "max-steps"
    try:
        while steps < max_steps:
            pc = state.pc & ~1
            isp = state.isp
            try:
                rec, state = hobbit_sem.step(state)
            except hobbit_sem.Refusal as exc:
                status = "REFUSED pc=%08x insn=%s: %s" % (
                    pc, " ".join("%04x" % p for p in exc.parcels), exc.reason)
                break
            m.state = state
            steps += 1
            if hri_file:
                hri_file.write(rec.line() + "\n")
            if rec.trap:
                # The model did the sequence's store, *(CSP) = PC (which
                # is why 1e's compiler keeps nothing in R0 across floating
                # point); PC = *(VB+12) is the handler, played here.
                kernel_entry_flush(state)
                if recorder:
                    recorder.begin("F", pc, 0, [0, 0, 0, 0])
                    m.rec = recorder
                names = fpi(m, state)
                m.rec = None
                if names:
                    k.fp_traps.append((pc, names))
                    for nm in names:
                        ops["fpi " + nm] += 1
                    if recorder:
                        recorder.end(state.pc, (state.psw >> 4) & 1, 0)
                    continue
                status = "TRAP pc=%08x insn=%04x: %s" % (pc, rec.insn0,
                                                         rec.reason)
                break
            if census:
                ops[mnemonic_key([rec.insn0])] += 1
            if state.isp != isp:                    # a KCALL retired
                num = m.word(isp - 12)
                saved_psw = m.word(isp - 4)
                kernel_entry_flush(state)
                if recorder:
                    recorder.begin("K", num, NARGS.get(SYSCALLS.get(num), 0),
                                   [m.word(state.sp + 4 + 4 * i)
                                    for i in range(4)])
                    m.rec = recorder
                try:
                    res = k.call(num, state.sp)
                finally:
                    m.rec = None
                k.trace.append((SYSCALLS.get(num, "?"), res))
                if verbose:
                    print("p9run: %s -> %s" % k.trace[-1], file=sys.stderr)
                if recorder:
                    recorder.end(res or 0, (saved_psw >> 4) & 1,
                                 1 if res is None else 0)
                if res is None:
                    status = "exits(%r)" % k.exit_msg
                    break
                m.set_word(state.sp + 4, res)
                state.pc = m.word(isp - 8)
                state.psw = saved_psw
                state.isp = isp
    except Stop as exc:
        status = str(exc)
    for f in k.fds.values():
        if f not in (None, "console"):
            f.close()
    if hri_file:
        hri_file.close()
    if recorder:
        page = lambda a: (a + 0xFFF) & ~0xFFF
        recorder.write(record, boot_memory, start,
                       [KPAGE, (0x1000, page(max(k.max_brk, bss_end))),
                        (USTKTOP - USTKSIZE, USTKTOP)])
    return status, steps, k, ops


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True, help="the process's file tree")
    ap.add_argument("--max-steps", type=int, default=50_000_000)
    ap.add_argument("--census", action="store_true",
                    help="print the instruction forms retired")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--record", metavar="FILE",
                    help="write the recording bsv/P9HostTb.bsv replays")
    ap.add_argument("--hri", metavar="FILE",
                    help="write the HRI trace, one line per retirement")
    ap.add_argument("binary")
    ap.add_argument("args", nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)
    name = os.path.basename(args.binary)
    status, steps, k, ops = run(args.binary, [name] + args.args, args.root,
                                args.max_steps, sys.stdout.buffer,
                                args.census, args.verbose,
                                record=args.record, hri=args.hri)
    sys.stdout.flush()
    print("p9run: %s after %d instructions, %d syscalls"
          % (status, steps, len(k.trace)), file=sys.stderr)
    if args.census:
        for key, n in sorted(ops.items(), key=lambda kv: -kv[1]):
            print("  %8d  %s" % (n, key), file=sys.stderr)
    return 0 if status == "exits('')" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
