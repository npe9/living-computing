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
import copy
import io
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

CHDIR = 0x80000000          # libc.h: mode bit for directories
DIRLEN = 116                # libc.h: the machine-independent Dir
NAMELEN = 28
EVE = "bootes"              # devcons.c:24 eve[]; devdir()'s uid and gid
PID = 1                     # the one process's pid (#c/pid)
RFNAMEG, RFENVG, RFFDG, RFNOTEG, RFPROC, RFMEM, RFNOWAIT = \
    1, 2, 4, 8, 16, 32, 64  # libc.h rfork flags
RFCNAMEG, RFCENVG, RFCFDG = 1 << 10, 1 << 11, 1 << 12
ERRLEN = 64                 # libc.h: Waitmsg.msg
EXEC = object()             # Kernel.call's "a new image" result
KERNDATE = 721110517        # `kerndate` in the shipped s9term; devdir's mtime


def convD2M(name, uid, gid, qpath, qvers, mode, atime, mtime, length,
            typ, dev):
    """sys/src/libc/9sys/convD2M.c, for a Dir with hlength 0."""
    def string(x):
        return x.encode("latin-1")[:NAMELEN - 1].ljust(NAMELEN, b"\0")
    out = string(name) + string(uid) + string(gid) + struct.pack(
        "<IIIIIIIHH", qpath & 0xFFFFFFFF, qvers, mode & 0xFFFFFFFF,
        atime & 0xFFFFFFFF, mtime & 0xFFFFFFFF, length & 0xFFFFFFFF, 0,
        typ, dev)
    assert len(out) == DIRLEN
    return out


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


class Stream:
    """Standard input or output when the caller redirects it (rc's `<`
    and `>`, or one end of a pipeline that `tools/p9kgen.py` runs a
    stage at a time).  Reads come from `data`; writes go to `sink`."""

    def __init__(self, name, data=b"", sink=None, dirent=None):
        self.name = name
        self.buf = io.BytesIO(data)
        self.sink = sink
        self.dirent = dirent    # what fstat says, for a device file

    def read(self, n):
        return self.buf.read(n)

    def write(self, data):
        self.sink.write(data)

    def close(self):
        pass


class Kernel:
    def __init__(self, root, machine, bss_end, console, stdin=None,
                 stdout=None):
        self.root = os.path.realpath(root)
        self.cwd = ""           # the working directory, relative to root
        self.m = machine
        self.brk = bss_end
        self.console = console
        # fd 0 reads as end of file unless stdin is given; fd 1 is the
        # console unless stdout is given; fd 2 is always the console.
        self.fds = {0: None if stdin is None else Stream("stdin", stdin),
                    1: "console" if stdout is None
                    else Stream("stdout", sink=stdout),
                    2: "console"}
        self.max_brk = bss_end
        self.errstr = b""
        self.trace = []
        self.fp_traps = []      # (pc, [mnemonics]) per handler entry
        self.exit_msg = None
        self.noteid = 1
        self.notify = 0
        # processes (sys_rfork with RFPROC, sys_exec, sys_wait)
        self.pid = PID
        self.pids = [PID]       # the last pid handed out, shared
        self.text = ""          # Proc.text: the program's name
        self.inherited = set()  # ids of fd objects a parent still holds
        self.waitq = []         # Waitmsg bytes of children that exited
        self.entry = None       # (ISP, PSW) at this kernel entry
        self.new_state = None   # the image sys_exec built
        self.max_steps = 0
        self.verbose = False
        self.recording = False
        self.child_steps = 0    # instructions retired by children
        self.children = []      # (pid, text, steps, trace, status)

    def host_path(self, name):
        # An absolute path is under --root; a relative one is under the
        # working directory (--cwd, itself a path under --root).
        if name.startswith("/"):
            rel = name.lstrip("/")
        else:
            rel = os.path.join(self.cwd, name)
        p = os.path.realpath(os.path.join(self.root, rel))
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
            if path.startswith("#"):
                return self.open_device(path, a[1])
            # libc.h: OREAD 0, OWRITE 1, ORDWR 2, OEXEC 3 (read, checking
            # execute permission); OTRUNC 16.  OCEXEC and ORCLOSE are not
            # modelled, and a mode with any other bit is refused rather
            # than quietly opened as something else.
            if a[1] & ~(3 | 16):
                raise Stop("p9run: refused open(%r, 0x%x): mode bits beyond "
                           "OREAD/OWRITE/ORDWR/OEXEC|OTRUNC" % (path, a[1]))
            mode = a[1] & 3
            try:
                f = open(self.host_path(path),
                         {0: "rb", 1: "r+b", 2: "r+b", 3: "rb"}[mode])
                if a[1] & 16:
                    f.close()
                    f = open(self.host_path(path), "w+b")
            except OSError as e:
                return self.fail("%s: %s" % (path, e.strerror))
            return self.new_fd(f)
        if name == "create":
            path = m.cstring(a[0]).decode("latin-1")
            # create(name, mode, perm): the file is made (or truncated) and
            # opened.  The same mode rule as open; a directory (CHDIR in
            # perm, 0x80000000) is refused.  A new file's permissions are
            # perm ANDed with the containing directory's, an existing
            # file's are unchanged (sys/man/2/open, `create`); strip
            # refuses a file without execute bits, so zl's 0775 matters.
            if (a[1] & ~(3 | 16)) or (a[2] & 0x80000000):
                raise Stop("p9run: refused create(%r, 0x%x, 0x%x)"
                           % (path, a[1], a[2]))
            host = self.host_path(path)
            new = not os.path.exists(host)
            try:
                f = open(host, "w+b")
            except OSError as e:
                return self.fail("%s: %s" % (path, e.strerror))
            if new:
                dirmode = os.stat(os.path.dirname(host)).st_mode
                os.chmod(host, a[2] & dirmode & 0o777)
            return self.new_fd(f)
        if name == "close":
            f = self.fds.pop(a[0], None)
            if f not in (None, "console") and id(f) not in self.inherited:
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
            if f == "console" or isinstance(f, Stream):
                if m.rec is not None:
                    m.rec.output("-", 0, a[1], a[2])
                (self.console if f == "console" else f).write(data)
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
            if isinstance(f, Stream):       # sysseek: a pipe is Eisstream
                return self.fail("seek on a stream")
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
        res = self.call_a3(name, a)
        if res is not None:
            return res
        raise Stop("p9run: refused syscall %d (%s) args %s"
                   % (num, name, " ".join("%08x" % x for x in a)))

    # ----------------------------------------------------------------
    # System calls added for A3's generated kernel inputs (awk, sed,
    # xd, grep, sort, strip run as rc's pipeline stages by
    # tools/p9kgen.py).  Kept apart from `call` so that other additions
    # merge cleanly.  Returns None for a call it does not do.
    # ----------------------------------------------------------------

    def call_a3(self, name, a):
        if name == "fstat":
            return self.sys_fstat(a)
        if name == "stat":
            return self.sys_stat(a)
        if name == "notify":
            return self.sys_notify(a)
        if name == "rfork":
            return self.sys_rfork(a)
        if name == "exec":
            return self.sys_exec(a)
        if name == "wait":
            return self.sys_wait(a)
        return None

    def open_device(self, path, mode):
        """open of a `#` name.  Two device files are modelled, because
        libc and APE startup code open them; any other is refused.

          #c/pid  devcons.c Qpid: readnum(offset, buf, n, pid, NUMSIZE),
                  the pid right-aligned in 11 characters and a blank
                  (libc getpid(), used by mktemp() in ar).  The pid is
                  PID.
          #e      devenv.c: the environment directory, read OREAD only;
                  the environment is empty here, so envgen() has no
                  entry and a read returns 0 bytes (APE _envsetup()
                  opendir()s it; libc getenv() opens #e/name).
        """
        if path == "#c/pid":
            if mode & 3 != 0:
                return self.fail("permission denied")   # consdir 0444
            text = ("%11d " % PID).encode()
            return self.new_fd(Stream(path, text, dirent=convD2M(
                "pid", EVE, EVE, 16, 0, 0o444, 0, KERNDATE, 12,
                ord("c"), 0)))
        if path in ("#e", "#e/"):
            if mode != 0:
                return self.fail("permission denied")   # Eperm
            # devstat with no entry and a CHDIR qid:
            # devdir(c, c->qid, ".", 0, eve, CHDIR|0700)
            return self.new_fd(Stream(path, b"", dirent=convD2M(
                ".", EVE, EVE, CHDIR, 0, CHDIR | 0o700, 0, KERNDATE, 0,
                ord("e"), 0)))
        if path.startswith("#e/"):
            return self.fail("file does not exist")     # Enonexist
        raise Stop("p9run: refused open(%r, %d): device not modelled"
                   % (path, mode))

    def sys_rfork(self, a):
        """sysproc.c sysrfork without RFPROC: new name, environment, fd
        or note groups for this process, then return 0.  This process is
        alone, so a new group is the old one (RFCFDG would close every
        fd and is refused; so is RFPROC, a new process)."""
        flag = a[0]
        if (flag & (RFNAMEG | RFCNAMEG)) == (RFNAMEG | RFCNAMEG) or \
                (flag & (RFENVG | RFCENVG)) == (RFENVG | RFCENVG):
            return self.fail("bad arg in system call")  # Ebadarg
        if flag & RFPROC:
            return self.fork(flag)
        if flag & RFCFDG:
            raise Stop("p9run: refused rfork(0x%x): RFCFDG not modelled"
                       % flag)
        if flag & (RFMEM | RFNOWAIT):
            return self.fail("bad arg in system call")  # Ebadarg
        if flag & RFNOTEG:
            self.noteid += 1
        return 0

    def fork(self, flag):
        """sysrfork with RFPROC.  The child is a copy of this process
        (dupseg of every segment: a copy of the memory, the registers and
        the stack cache's array) that returns 0 from the call; the parent
        gets the child's pid.  The child runs first, to its exits, before
        the parent goes on: one processor and no clock here, and a parent
        that waits (rl's fexec, rc) sees what it would have seen.  A
        program whose parent and child must run interleaved (a pipe
        between them) is outside that and will stop or deadlock loudly
        on its own refused call.

        Fd groups: RFFDG gives the child a copy of the table that holds
        the same channels (so the same offsets, dupfgrp); without it the
        table itself is shared.  RFCFDG and RFMEM are refused."""
        if flag & (RFCFDG | RFMEM):
            raise Stop("p9run: refused rfork(0x%x): RFCFDG/RFMEM not "
                       "modelled" % flag)
        if self.recording:
            raise Stop("p9run: refused rfork(0x%x): a second process "
                       "cannot be recorded for the Bluespec run" % flag)
        isp, saved_psw = self.entry
        cstate = copy.deepcopy(self.m.state)
        cm = Machine(cstate)
        cm.set_word(cstate.sp + 4, 0)           # the child's rfork() = 0
        cstate.pc = cm.word(isp - 8)
        cstate.psw = saved_psw
        cstate.isp = isp
        ck = Kernel(self.root, cm, self.brk, self.console)
        ck.cwd = self.cwd
        ck.brk, ck.max_brk = self.brk, self.max_brk
        self.pids[0] += 1
        ck.pid = self.pids[0]
        ck.pids = self.pids
        ck.text = self.text
        ck.noteid = self.noteid if not flag & RFNOTEG else self.noteid + 1
        ck.max_steps, ck.verbose = self.max_steps, self.verbose
        if flag & RFFDG:
            ck.fds = dict(self.fds)
            ck.inherited = self.inherited | {id(f) for f in self.fds.values()}
        else:
            ck.fds = self.fds
            ck.inherited = self.inherited
        status, steps = process_loop(cstate, cm, ck, self.max_steps, None,
                                     None, False, self.verbose,
                                     collections.Counter())
        self.child_steps += steps + ck.child_steps
        self.children.append((ck.pid, ck.text, steps, ck.trace, status))
        if not status.startswith("exits("):
            raise Stop("p9run: child %d (%s) stopped: %s"
                       % (ck.pid, ck.text, status))
        if flag & RFFDG:
            for f in ck.fds.values():
                if f not in (None, "console") and id(f) not in ck.inherited:
                    f.close()
        # proc.c pexit(): the Waitmsg -- pid and three times by readnum
        # (NUMSIZE 12 each), then "text pid:exitstr" or "" in msg[ERRLEN]
        if not flag & RFNOWAIT:
            msg = ("%s %d:%s" % (ck.text, ck.pid, ck.exit_msg)
                   if ck.exit_msg else "").encode("latin-1")[:ERRLEN - 1]
            self.waitq.append(("%11d " % ck.pid).encode()
                              + ("%11d " % 0).encode() * 3
                              + msg.ljust(ERRLEN, b"\0"))
        return ck.pid

    def ns_path(self, name):
        """The 1e name space for exec: lib/namespace binds /$cputype/bin
        on /bin and unions /rc/bin after it.  Only /hobbit/bin is in a
        tree here; /rc/bin (rc scripts) is not modelled."""
        if name.startswith("/bin/"):
            return self.host_path("/hobbit" + name)
        return self.host_path(name)

    def sys_exec(self, a):
        """sysproc.c sysexec(file, argv): namec(file, OEXEC), the Exec
        header checked (Z_MAGIC, entry within the text), the arguments
        copied out of the old image, a new image built (`process_image`:
        the same exec frame as the first process's) and the old one
        discarded; Proc.text = the file's last element.  `#!` files are
        refused (rc is not run here)."""
        path = self.m.cstring(a[0]).decode("latin-1")
        argv = []
        p = a[1]
        while self.m.word(p):
            argv.append(self.m.cstring(self.m.word(p)).decode("latin-1"))
            p += 4
        host = self.ns_path(path)
        if not os.path.isfile(host):
            return self.fail("file does not exist")     # Enonexist
        with open(host, "rb") as f:
            head = f.read(32)
        if head[:2] == b"#!":
            raise Stop("p9run: refused exec(%r): #! scripts not modelled"
                       % path)
        if len(head) < 32 or int.from_bytes(head[:4], "big") not in \
                p9exec.MAGIC:
            return self.fail("exec header invalid")     # Ebadexec
        state, bss_end = process_image(host, argv)
        self.brk = self.max_brk = bss_end
        self.text = os.path.basename(path)[:NAMELEN - 1]
        self.new_state = state
        return EXEC

    def sys_wait(self, a):
        """sysproc.c syswait -> proc.c pwait: no children and no wait
        records is Enochild; otherwise the first record is copied out
        and its pid returned.  Children have all run to completion."""
        if not self.waitq:
            return self.fail("no living children")      # Enochild
        w = self.waitq.pop(0)
        if a[0]:
            self.m.set_bytes(a[0], w)
        return int(w[:12])

    def sys_notify(self, a):
        """sysproc.c sysnotify: u->notify = arg[0]; return 0.  No note is
        ever posted to a process here, so the handler is only kept."""
        self.notify = a[0]
        return 0

    def dir_entry(self, f):
        """The 116-byte machine-independent Dir that a device's stat
        routine writes (sys/include/libc.h struct Dir, DIRLEN 116;
        sys/src/libc/9sys/convD2M.c: three NAMELEN strings, then
        qid.path, qid.vers, mode, atime, mtime as little-endian longs,
        the length as eight bytes with the high word zero, type and dev
        as shorts).  `f` is an open file's host object, a host path, a
        Stream, or "console"."""
        if f == "console":
            # devcons.c consstat: devstat(c, dp, consdir, NCONS, devgen)
            # finds "cons", {Qcons} = 3, length 0, perm 0660; dev.c
            # devdir() sets type = devchar ('c') and mtime = kerndate.
            return convD2M("cons", EVE, EVE, 3, 0, 0o660, 0, KERNDATE, 0,
                           ord("c"), 0)
        if isinstance(f, Stream) and f.dirent is not None:
            return f.dirent
        if isinstance(f, Stream):
            # devpipe.c pipestat -> stream.c streamstat(c, db, "pipe",
            # 0666) -> devdir with the channel's qid, STREAMQID(id,
            # Sdataqid) = (id<<5)|31 (portdat.h), and the bytes queued.
            # The length is 0 here: what a reader sees before the
            # writer has written.
            return convD2M("pipe", EVE, EVE, (1 << 5) | 31, 0, 0o666, 0,
                           KERNDATE, 0, ord("|"), 0)
        # A host file is what the file server says through devmnt (type
        # 'M'): the name, the permission bits with CHDIR for a
        # directory, the length and the times.
        path = f if isinstance(f, str) else f.name
        st = os.stat(path)
        isdir = os.path.isdir(path)
        qpath = (st.st_ino & 0x7FFFFFFF) | (CHDIR if isdir else 0)
        mode = (st.st_mode & 0o777) | (CHDIR if isdir else 0)
        name = "/" if os.path.realpath(path) == self.root \
            else os.path.basename(path)
        return convD2M(name, EVE, EVE, qpath, 0, mode,
                       int(st.st_atime), int(st.st_mtime),
                       0 if isdir else st.st_size, ord("M"), 0)

    def sys_fstat(self, a):
        """sysfile.c sysfstat(fd, buf): the device's stat of the fd's
        channel into buf (DIRLEN bytes)."""
        f = self.fds.get(a[0], "absent")
        if f == "absent":
            return self.fail("fd out of range or not open")   # Ebadfd
        if f is None:                   # fd 0 with no stdin given
            raise Stop("p9run: refused fstat(0): standard input is not "
                       "redirected (give stdin=)")
        self.m.set_bytes(a[1], self.dir_entry(f))
        return 0

    def sys_stat(self, a):
        """sysfile.c sysstat(name, buf): namec, then the device's stat.
        Only the file tree is modelled; a `#` device name is refused."""
        path = self.m.cstring(a[0]).decode("latin-1")
        if path.startswith("#"):
            raise Stop("p9run: refused stat(%r): devices are not modelled"
                       % path)
        host = self.host_path(path)
        if not os.path.exists(host):
            return self.fail("file does not exist")     # Enonexist
        self.m.set_bytes(a[1], self.dir_entry(host))
        return 0


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
        record=None, hri=None, cwd="", stdin=None, stdout=None):
    """Run `binary`; optionally write the Bluespec run's recording and
    the HRI trace (one line per retirement, the comparison's reference).

    `stdin` (bytes) is what fd 0 reads, end of file when None; `stdout`
    (a binary file object) receives fd 1, which is otherwise the console.
    """
    state, bss_end = process_image(binary, argv)
    m = Machine(state)
    k = Kernel(root, m, bss_end, console, stdin, stdout)
    k.cwd = cwd.strip("/")
    k.text = os.path.basename(binary)
    k.max_steps = max_steps
    k.verbose = verbose
    k.recording = bool(record)
    recorder = Recorder() if record else None
    boot_memory = dict(state.memory) if record else None
    start = (state.pc, state.sp, state.psw, state.isp, state.vb)
    hri_file = open(hri, "w") if hri else None
    ops = collections.Counter()
    status, steps = process_loop(state, m, k, max_steps, recorder, hri_file,
                                 census, verbose, ops)
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


def process_image(binary, argv):
    """A new process image for `binary` (the file attached, the exec
    frame built, the kernel page's stubs laid out): (state, bss_end)."""
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
    return state, bss_end


def process_loop(state, m, k, max_steps, recorder, hri_file, census,
                 verbose, ops):
    """Run the process in `state` until it exits or stops: (status,
    instructions retired).  An exec replaces the image and goes on."""
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
                k.entry = (isp, saved_psw)
                try:
                    res = k.call(num, state.sp)
                finally:
                    m.rec = None
                if res is EXEC:                     # sysexec: a new image
                    k.trace.append(("exec", 0))
                    state = k.new_state
                    m.state = state
                    continue
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
    return status, steps


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True, help="the process's file tree")
    ap.add_argument("--max-steps", type=int, default=50_000_000)
    ap.add_argument("--census", action="store_true",
                    help="print the instruction forms retired")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--cwd", default="", metavar="DIR",
                    help="the working directory, as a path under --root")
    ap.add_argument("--record", metavar="FILE",
                    help="write the recording bsv/P9HostTb.bsv replays")
    ap.add_argument("--hri", metavar="FILE",
                    help="write the HRI trace, one line per retirement")
    ap.add_argument("--stdin", metavar="FILE",
                    help="a host file for fd 0 (default: end of file)")
    ap.add_argument("--stdout", metavar="FILE",
                    help="a host file for fd 1 (default: the console)")
    ap.add_argument("binary")
    ap.add_argument("args", nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)
    name = os.path.basename(args.binary)
    stdin = pathlib.Path(args.stdin).read_bytes() if args.stdin else None
    stdout = open(args.stdout, "wb") if args.stdout else None
    status, steps, k, ops = run(args.binary, [name] + args.args, args.root,
                                args.max_steps, sys.stdout.buffer,
                                args.census, args.verbose,
                                record=args.record, hri=args.hri,
                                cwd=args.cwd, stdin=stdin, stdout=stdout)
    if stdout:
        stdout.close()
    sys.stdout.flush()
    print("p9run: %s after %d instructions, %d syscalls"
          % (status, steps, len(k.trace)), file=sys.stderr)
    if args.census:
        for key, n in sorted(ops.items(), key=lambda kv: -kv[1]):
            print("  %8d  %s" % (n, key), file=sys.stderr)
    return 0 if status == "exits('')" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
