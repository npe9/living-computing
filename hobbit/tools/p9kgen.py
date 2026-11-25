#!/usr/bin/env python3
"""Make the 1e kernel's generated inputs for a configuration, using the
release's own tools on the reference model.

What `sys/src/9/hobbit/mkfile` and `sys/src/9/port/portmkfile` generate
for `mk 9term` (the configuration the shipped kernel `hobbit/s9term` was
linked from), and how each is made here:

  term.c            rc ../port/mkdevc term > term.c
  term.z            zc -w -Dram -DKERNDATE=... term.c (the 9term rule's
                    first command; shows term.c compiles)
  devtab.h          rc ../port/mkdevh $CONFLIST > devtab.h
  errstr.h          rc ../port/mkerrstr > errstr.h
  objlists          the `DEV=`, `STREAM=`, `MISC=` backquotes of the
                    mkfile: rc ../port/mk{dev,stream,misc}list term
  init.h            za initcode; zl -l -s -o init.out -H2 -T0x1020 -R4
                    initcode.z; {echo; xd -r -1x init.out | sed; echo}
  bootterm.c        ../boot/mkboot term > bootterm.c
  bootterm.root.c   zc bootterm.c; libboot.az (`mk` in ../boot: zc each
                    file, `ar vu`, `rl`); zl -o bootterm.out bootterm.z
                    ../boot/libboot.az print.z -lauth;
                    ../port/mkroot bootterm boot (strip; xd -1x | sed)
  bootterm.root.z   zc -w -Dram bootterm.root.c
  KERNDATE          `date -n` at link time.  Not run: the value baked into
                    s9term's `kerndate` is read back (721110517,
                    1992-11-07 04:28:37 GMT) and written to kerndate.

Every program that runs is a shipped Hobbit binary of the release
(tools/plan9-1e/hobbit/bin) executed by `tools/p9run.py` on
`sem/hobbit_sem.py`.  Python plays only rc: it lays out each script's
pipeline, runs one stage to completion with its standard output in a
buffer, and gives that buffer to the next stage as its standard input
(a pipe with infinite capacity; every stage here reads its input to the
end before the next one needs it).  The awk and sed programs are not
retyped: they are lifted out of the vendored rc scripts by `rc_pieces`
(single-quoted words and here-documents, comments skipped) and joined
with the variables rc would substitute (`$O` = `z` from hobbit/mkfile,
`$n`, `$field`, `$1`), exactly where the script's free carets put them.

`rl` makes `__.SYMDEF` and then forks and execs `/bin/ar` itself
(rl.c `fexec`); that is a fork/exec/wait inside p9run, not rc.

`rc ../port/mksystab` is run only up to its first `sam -d` (there is no
sam here): that half is compared with the start of the shipped
`../port/systab.h`, which is used as it is (it is the generated file;
mk would remake it only if sys.h were newer).

Checked against what the release ships (`check`): errstr.h = the
shipped hobbit/errstr.h; init.h = `initcode[]` in s9term's data;
term.c's `devtab[]` = s9term's, entry by entry through its symbol
table, and its `devchar` and `conffile`; bootterm.root.c against
s9term's `bootcode[]` (it differs: see docs/plan9_boot_plan.md A3).

The work is done in a copy of the vendored tree under OUT/root, laid out
like the release (`/sys/include`, `/hobbit/include`, `/hobbit/lib`,
`/sys/src/9/{port,hobbit,boot}`, `/sys/src/libc/9syscall`); the products
are then copied to OUT/.  OUT/p9kgen.log records every program run, its
arguments, instruction count, system calls and wall time.

    python3 tools/p9kgen.py --out /tmp/kgen [--conf term] [--no-boot]
    python3 tools/p9kgen.py --out K --conf rom    # TYPE=rom: -Drom
"""

import argparse
import io
import os
import pathlib
import shutil
import struct
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import p9exec  # noqa: E402
import p9run   # noqa: E402

REL = HERE / "plan9-1e"
BIN = REL / "hobbit" / "bin"
S9TERM = REL / "hobbit" / "s9term"
CONFLIST = ["cpu", "term", "termlocal", "bart", "rom"]  # hobbit/mkfile
O = "z"                                                # hobbit/mkfile: O=z
CFLAGS = ["-w", "-Dram"]                               # -w -D$TYPE, TYPE=ram


def default_type(conf):
    """$TYPE for a configuration: the mkfile's default `ram`, except
    `rom`, whose rule (9rom: roml.$O, lib$TYPE.a) and rommain.c need
    `mk CONF=rom TYPE=rom 9rom` (docs/boot_rom.md: an assumption -- the
    mkfile does not say how it was invoked)."""
    return "rom" if conf == "rom" else "ram"


def cflags(ktype):
    """hobbit/mkfile: CFLAGS=-w -D$TYPE."""
    return ["-w", "-D" + ktype]
BOOT_CFLAGS = ["-w"]                                   # boot/mkfile
BOOT_OFILES = ["async", "aux", "boot", "bboot", "dosboot", "bri", "cache",
               "cyc", "datakit", "dk", "getpasswd", "hybrid", "ip", "key",
               "local", "newkernel", "nopsession", "romboot", "settime",
               "userpasswd"]                           # boot/mkfile OFILES
MAX_STEPS = 2_000_000_000

#: the subtrees of the release the scripts and compilers read
TREE = ["sys/include", "hobbit/include", "hobbit/lib", "hobbit/mkfile",
        "hobbit/bin",
        "sys/src/libc/9syscall", "sys/src/9/port", "sys/src/9/hobbit",
        "sys/src/9/boot"]


# --------------------------------------------------------------------
# rc's quoting, read out of the scripts
# --------------------------------------------------------------------

def rc_pieces(path):
    """The single-quoted words and here-document bodies of an rc script,
    in order, as ("q", text) / ("h", text).  rc: a quoted word runs to the
    next lone quote, '' inside it is one quote; `#` at the start of a word
    begins a comment; `<<'eof'` (or <<eof) takes the following lines up to
    a line `eof`.  Unquoted here-documents are returned unexpanded."""
    t = pathlib.Path(path).read_text(encoding="latin-1")
    out = []
    i = 0
    pending = []            # here-document delimiters seen on this line
    while i < len(t):
        c = t[i]
        if c == "'":
            j = i + 1
            buf = []
            while True:
                if t[j] == "'":
                    if j + 1 < len(t) and t[j + 1] == "'":
                        buf.append("'")
                        j += 2
                        continue
                    break
                buf.append(t[j])
                j += 1
            out.append(("q", "".join(buf)))
            i = j + 1
        elif c == "#" and (i == 0 or t[i - 1] in " \t\n"):
            i = t.index("\n", i)
        elif t.startswith("<<", i):
            j = i + 2
            if t[j] == "'":
                k = t.index("'", j + 1)
                pending.append(t[j + 1:k])
                i = k + 1
            else:
                k = j
                while t[k] not in " \t\n|;":
                    k += 1
                pending.append(t[j:k])
                i = k
        elif c == "\n" and pending:
            i += 1
            for delim in pending:
                end = t.index("\n" + delim + "\n", i - 1)
                out.append(("h", t[i:end + 1]))
                i = end + len(delim) + 2
            pending = []
        else:
            i += 1
    return out


def piece(pieces, index, kind, starts):
    k, text = pieces[index]
    if k != kind or not text.startswith(starts):
        raise SystemExit("p9kgen: rc script piece %d is %s %r, expected %s "
                         "starting %r" % (index, k, text[:40], kind, starts))
    return text


# --------------------------------------------------------------------
# rc's part: run a program, run a pipeline
# --------------------------------------------------------------------

class Rc:
    def __init__(self, root, log):
        self.root = pathlib.Path(root)
        self.log = log
        self.runs = []

    def run(self, prog, args, stdin=None, cwd="sys/src/9/hobbit",
            want=""):
        """Run one program to completion; return (stdout, exit string)."""
        out = io.BytesIO()
        err = io.BytesIO()
        t0 = time.time()
        status, steps, k, _ops = p9run.run(
            str(BIN / prog), [prog] + list(args), str(self.root), MAX_STEPS,
            err, cwd=cwd, stdin=stdin, stdout=out)
        dt = time.time() - t0
        steps += k.child_steps          # rl's fork of ar counts too
        shown = " ".join(a if a.isprintable() and len(a) < 40
                         else repr(a[:24]) + "..." for a in args)
        line = "%-6s %-40s %12d instr %4d syscalls %8.1f s  %s" % (
            prog, shown[:60], steps, len(k.trace), dt, status)
        self.runs.append((prog, args, steps, len(k.trace), dt, status))
        self.log.write(line + "\n")
        self.log.flush()
        if err.getvalue():
            self.log.write("       fd 2: %r\n" % err.getvalue()[:400])
        if not status.startswith("exits("):
            raise SystemExit("p9kgen: %s %s: %s\n%s" % (
                prog, " ".join(args), status, err.getvalue().decode(
                    "latin-1")))
        if want is not None and k.exit_msg != want:
            raise SystemExit("p9kgen: %s %s exited %r\n%s" % (
                prog, " ".join(args), k.exit_msg,
                err.getvalue().decode("latin-1")))
        return out.getvalue(), k.exit_msg

    def pipe(self, *stages, stdin=None, cwd="sys/src/9/hobbit"):
        """a | b | c: each stage runs to completion and its standard
        output is the next one's standard input."""
        data = stdin
        for prog, args in stages:
            data, _st = self.run(prog, args, stdin=data, cwd=cwd)
        return data

    def echo(self, *words):
        return self.run("echo", list(words))[0]

    def cat_heredoc(self, text):
        # rc writes a here-document to a temporary file and makes it the
        # command's standard input; cat copies it.
        return self.run("cat", [], stdin=text.encode("latin-1"))[0]


# --------------------------------------------------------------------
# The scripts of sys/src/9/port and sys/src/9/boot
# --------------------------------------------------------------------

PORT = REL / "sys" / "src" / "9" / "port"
BOOT = REL / "sys" / "src" / "9" / "boot"


def mkextract(rc, field, n, files, unique=False):
    """../port/mkextract [-u] field n file...: the awk `select`, then
    `sort -u` with -u."""
    p = rc_pieces(PORT / "mkextract")
    prog = (piece(p, 1, "q", "\n\n\t\tBEGIN") + str(n) +
            piece(p, 2, "q", " }\n\t\t$0 ~ \"^") + field +
            piece(p, 3, "q", "\"\t{ doprint=1; next }"))
    out = rc.run("awk", [prog] + list(files))[0]
    if unique:
        out = rc.run("sort", ["-u"], stdin=out)[0]
    return out


def mklist(rc, script, field, conf):
    """../port/mk{dev,stream,misc}list conf: its own `fn mkextract`,
    `sed '/^$/d; /^#/d' $2 | awk '...'.$O'...' 'field=^'$1`."""
    p = rc_pieces(PORT / script)
    sed = piece(p, 0, "q", "/^$/d")
    qs = [text for kind, text in p[1:-1]]
    prog = ("." + O).join(qs)        # each '...'.$O'...' join is `.z`
    field_arg = piece(p, len(p) - 1, "q", "field=^") + field
    return rc.pipe(("sed", [sed, conf]), ("awk", [prog, field_arg]))


def mkdevc(rc, conf):
    p = rc_pieces(PORT / "mkdevc")
    out = rc.cat_heredoc(piece(p, 0, "h", "#include\t\"u.h\""))
    out += rc.run("awk", [piece(p, 1, "q", "{\n\tprint \"\t{ \"")],
                  stdin=mkextract(rc, "dev", 0, [conf]))[0]
    out += rc.echo(piece(p, 2, "q", "};"))
    out += rc.run("awk", [piece(p, 3, "q", "\n\tBEGIN{\n\t\tprintf")],
                  stdin=mkextract(rc, "dev", 0, [conf]))[0]
    out += rc.run("awk", [piece(p, 4, "q", "\n\t{\tprint \"extern")],
                  stdin=mkextract(rc, "stream", 0, [conf]))[0]
    out += rc.run("awk", [piece(p, 5, "q", "\n\tBEGIN{\tprint \"void")],
                  stdin=mkextract(rc, "stream", 0, [conf]))[0]
    out += mkextract(rc, "port", 0, [conf])
    # if(! grep conffile $* > /dev/null) echo 'char *conffile = "'$1'";'
    _o, status = rc.run("grep", ["conffile", conf], want=None)
    if status != "":
        out += rc.echo(piece(p, 6, "q", "char\t*conffile") + conf +
                       piece(p, 7, "q", "\";"))
    out += rc.echo(piece(p, 8, "q", "ulong\tkerndate"))
    return out


def mkdevh(rc, confs):
    p = rc_pieces(PORT / "mkdevh")
    return rc.run("awk", [piece(p, 0, "q", "{\n\tprint \"void")],
                  stdin=mkextract(rc, "dev", 1, confs, unique=True))[0]


def mkerrstr(rc):
    p = rc_pieces(PORT / "mkerrstr")
    stdin = (rc.root / "sys/src/9/port/error.h").read_bytes()
    return rc.run("sed", [piece(p, 0, "q", "s/extern //")], stdin=stdin)[0]


def xd_to_c(rc, xd_args, sed_pieces):
    """`xd ... | sed -e 's/^[0-9a-f]+ //' -e 's/ ([0-9a-f][0-9a-f])/0x\\1,/g'`"""
    return rc.pipe(("xd", xd_args),
                   ("sed", ["-e", sed_pieces[0], "-e", sed_pieces[1]]))


def mkroot(rc, name, cname):
    """../port/mkroot name cname, in the hobbit directory."""
    p = rc_pieces(PORT / "mkroot")
    rc.run("strip", [name + ".out"])
    out = rc.echo(piece(p, 0, "q", "unsigned char ") + cname +
                  piece(p, 1, "q", "code[]={"))
    out += xd_to_c(rc, ["-1x", name + ".out"],
                   [piece(p, 2, "q", "s/^"), piece(p, 3, "q", "s/ (")])
    out += rc.echo(piece(p, 4, "q", "};"))
    out += rc.echo(piece(p, 5, "q", "long ") + cname +
                   piece(p, 6, "q", "len = sizeof ") + cname +
                   piece(p, 7, "q", "code;"))
    return out


def mkboot(rc, conf):
    """../boot/mkboot conf, run in the hobbit directory."""
    p = rc_pieces(BOOT / "mkboot")
    out = rc.cat_heredoc(piece(p, 0, "h", "#include <u.h>"))
    out += rc.run("awk", [piece(p, 1, "q", "{\n\tprintf")],
                  stdin=mkextract(rc, "boot", 0, [conf]))[0]
    out += rc.cat_heredoc(piece(p, 2, "h", "\t{ 0 },"))
    out += rc.run("awk", [piece(p, 3, "q", "\n\tBEGIN\t{ cpuflag"), conf])[0]
    out += rc.run("awk", [piece(p, 4, "q", "\n\tBEGIN\t\t\t{ cfs")],
                  stdin=mkextract(rc, "misc", 0, [conf]))[0]
    return out


def mkfile_init_h(rc):
    """hobbit/mkfile's init.h rule."""
    rc.run("za", ["initcode"])
    rc.run("zl", ["-l", "-s", "-o", "init.out", "-H2", "-T0x1020", "-R4",
                  "initcode." + O])
    # the rule's sed expressions are the same two as mkroot's
    p = rc_pieces(PORT / "mkroot")
    out = rc.echo("uchar initcode[]={")
    out += xd_to_c(rc, ["-r", "-1x", "init.out"],
                   [piece(p, 2, "q", "s/^"), piece(p, 3, "q", "s/ (")])
    out += rc.echo("};")
    return out


def build_libboot(rc):
    """`mk` in ../boot: zc -w each OFILE, `ar vu libboot.az names`, `rl`."""
    cwd = "sys/src/9/boot"
    for f in BOOT_OFILES:
        rc.run("zc", BOOT_CFLAGS + [f + ".c"], cwd=cwd)
    names = [f + "." + O for f in BOOT_OFILES]
    rc.run("ar", ["vu", "libboot.a" + O] + names, cwd=cwd)
    rc.run("rl", ["libboot.a" + O], cwd=cwd)


# --------------------------------------------------------------------
# The oracle: what the shipped kernel holds
# --------------------------------------------------------------------

def s9term():
    """The shipped kernel: its -H1 header (zl/asm.c, HEADR 80), data
    segment and symbols."""
    b = S9TERM.read_bytes()
    w = struct.unpack(">20I", b[:80])
    text, data, syms_off = w[6], w[7], 80 + w[6] + w[7]
    syms = p9exec.symbols({"blob": b, "sym_off": syms_off, "syms": w[3]})
    base = w[11]

    def at(addr, n):
        o = 80 + text + addr - base
        return b[o:o + n]
    return syms, at, base, base + data


def kernel_array(name, length):
    """The bytes of `name` in s9term's data, and the gap to the next
    data symbol (so a shorter array cannot pass as a prefix)."""
    syms, at, _lo, hi = s9term()
    addr = syms[name][0]
    nxt = min([v for v, t in syms.values() if t in "dD" and v > addr] + [hi])
    return at(addr, length), nxt - addr


def c_bytes(text):
    """The 0x.. initializers of a generated array, in order."""
    body = text.split("{", 1)[1].split("}", 1)[0]
    return bytes(int(x, 16) for x in body.replace("\n", "").split(",")
                 if x.strip())


def kerndate():
    syms, at, _lo, _hi = s9term()
    return int.from_bytes(at(syms["kerndate"][0], 4), "little")


# --------------------------------------------------------------------

def make_tree(root):
    for rel in TREE:
        src = REL / rel
        dst = pathlib.Path(root) / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)
    # lib/namespace: bind -c /usr/$user/tmp /tmp; ar's and sort's
    # temporary files go there
    (pathlib.Path(root) / "tmp").mkdir()


def generate(out, conf="term", boot=True, log=sys.stderr, ktype=None):
    CFLAGS = cflags(ktype or default_type(conf))
    out = pathlib.Path(out)
    root = out / "root"
    if root.exists():
        shutil.rmtree(root)
    make_tree(root)
    rc = Rc(root, log)
    k = root / "sys/src/9/hobbit"
    products = {}

    def product(name, data):
        (k / name).write_bytes(data)
        products[name] = data

    product("errstr.h", mkerrstr(rc))
    product("systab.h-head", mksystab_head(rc))
    product("devtab.h", mkdevh(rc, CONFLIST))
    product(conf + ".c", mkdevc(rc, conf))
    lists = b""
    for var, script, field in (("DEV", "mkdevlist", "dev"),
                               ("STREAM", "mkstreamlist", "stream"),
                               ("MISC", "mkmisclist", "misc")):
        words = mklist(rc, script, field, conf).split()
        lists += var.encode() + b"=" + b" ".join(words) + b"\n"
    product("objlists", lists)
    product("init.h", mkfile_init_h(rc))
    product("kerndate", b"%d\n" % kerndate())
    # The 9term rule's first command: $CC $CFLAGS '-DKERNDATE='`{date -n}
    # $CONF.c -- run here to show the generated file compiles.
    rc.run("zc", CFLAGS + ["-DKERNDATE=%d" % kerndate(), conf + ".c"])
    product(conf + "." + O, (k / (conf + "." + O)).read_bytes())
    if boot:
        product("boot%s.c" % conf, mkboot(rc, conf))
        rc.run("zc", CFLAGS + ["boot%s.c" % conf])
        build_libboot(rc)
        rc.run("zc", CFLAGS + ["-I.", "../port/print.c"])
        rc.run("zl", ["-o", "boot%s.out" % conf, "boot%s.%s" % (conf, O),
                      "../boot/libboot.a" + O, "print." + O, "-lauth"])
        product("boot%s.root.c" % conf, mkroot(rc, "boot" + conf, "boot"))
        rc.run("zc", CFLAGS + ["boot%s.root.c" % conf])
        product("boot%s.root.%s" % (conf, O),
                (k / ("boot%s.root.%s" % (conf, O))).read_bytes())
    for name, data in products.items():
        (out / name).write_bytes(data)
    return products, rc


def check(products, conf="term"):
    """Compare what can be compared with what the release ships."""
    report = []
    shipped = (REL / "sys/src/9/hobbit/errstr.h").read_bytes()
    report.append(("errstr.h = shipped hobbit/errstr.h",
                   products["errstr.h"] == shipped))
    if conf == "term":
        mine = c_bytes(products["init.h"].decode("latin-1"))
        theirs, room = kernel_array("initcode", len(mine))
        report.append(("init.h = s9term initcode[] (%d bytes, %d before "
                       "the next symbol)" % (len(mine), room),
                       mine == theirs and len(mine) <= room < len(mine) + 4))
        report += check_term_c(products["term.c"].decode("latin-1"))
        if "bootterm.root.c" in products:
            mine = c_bytes(products["bootterm.root.c"].decode("latin-1"))
            syms, at, _lo, _hi = s9term()
            n = int.from_bytes(at(syms["bootlen"][0], 4), "little")
            theirs, room = kernel_array("bootcode", n)
            hm = struct.unpack(">8I", mine[:32])
            ht = struct.unpack(">8I", theirs[:32])
            report.append(("bootterm.root.c = s9term bootcode[] (%d bytes, "
                           "text %#x data %#x bss %#x entry %#x; s9term: "
                           "bootlen %d, text %#x data %#x bss %#x entry %#x)"
                           % ((len(mine),) + hm[1:4] + (hm[5], n) + ht[1:4]
                              + (ht[5],)),
                           mine == theirs and len(mine) == n))
    if "systab.h-head" in products:
        shipped = (REL / "sys/src/9/port/systab.h").read_bytes()
        report.append(("mksystab's first half (cat; sed | tr | sed) = the "
                       "first %d bytes of shipped port/systab.h"
                       % len(products["systab.h-head"]),
                       shipped.startswith(products["systab.h-head"])))
    return report


def check_term_c(text):
    """term.c against s9term: every devtab[] pointer resolved through
    the kernel's symbol table, the devchar runes, conffile."""
    syms, at, _lo, _hi = s9term()
    names = {v: n for n, (v, t) in syms.items() if t in "Tt"}
    body = text.split("Dev\tdevtab[]={", 1)[1].split("};", 1)[0]
    mine = [w.strip() for w in body.replace("{", "").replace("}", "")
            .split(",") if w.strip()]
    base = syms["devtab"][0]
    theirs = [names.get(int.from_bytes(at(base + 4 * i, 4), "little"), "?")
              for i in range(len(mine) + 13)]
    out = [("term.c devtab[] = s9term devtab[] (%d entries, by symbol; "
            "the next word is %r)" % (len(mine) // 13, theirs[len(mine)]),
            theirs[:len(mine)] == mine and theirs[len(mine)] == "?")]
    runes = text.split('devchar=L"', 1)[1].split('"', 1)[0]
    ptr = int.from_bytes(at(syms["devchar"][0], 4), "little")
    # The characters are compared.  Their width is not: s9term holds this
    # L"" string one byte per character, NUL-ended, where the shipped zc
    # emits 16-bit little-endian runes (u.h: Rune is ushort) -- observed
    # 2026-11-23 with `zc` on `unsigned short *x = L"..."`.  So s9term's
    # data was not made by this zc with these headers.
    out.append(("term.c devchar = s9term devchar (%r; s9term stores one "
                "byte per character, the shipped zc two)" % runes,
                at(ptr, len(runes) + 1) == runes.encode() + b"\0"))
    conf = text.split('*conffile = "', 1)[1].split('"', 1)[0]
    ptr = int.from_bytes(at(syms["conffile"][0], 4), "little")
    out.append(("term.c conffile = s9term conffile (%r)" % conf,
                at(ptr, len(conf) + 1) == conf.encode() + b"\0"))
    return out


def mksystab_head(rc):
    """../port/mksystab up to its first `sam -d`: the here-document, then
    sed '...' sys.h | tr A-Z a-z | sed 's/.*/Syscall &;/g', then the next
    here-document.  The sam halves are not run (no sam here)."""
    p = rc_pieces(PORT / "mksystab")
    out = rc.cat_heredoc(piece(p, 0, "h", "#undef\tCHDIR"))
    out += rc.pipe(("sed", [piece(p, 1, "q", "s/#define"),
                            "/sys/src/libc/9syscall/sys.h"]),
                   ("tr", ["A-Z", "a-z"]),
                   ("sed", [piece(p, 2, "q", "s/.*/Syscall")]))
    out += rc.cat_heredoc(piece(p, 3, "h", "Syscall\tsysdeath;"))
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="the build directory")
    ap.add_argument("--conf", default="term")
    ap.add_argument("--type", help="$TYPE (default ram; rom for "
                    "--conf rom): CFLAGS -D$TYPE")
    ap.add_argument("--no-boot", action="store_true",
                    help="skip the boot program (zc, ar, zl: the long part)")
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "p9kgen.log", "w") as log:
        t0 = time.time()
        products, rc = generate(out, args.conf, not args.no_boot, log,
                                args.type)
        report = check(products, args.conf)
        total = sum(r[2] for r in rc.runs)
        log.write("total: %d programs, %d instructions, %.1f s\n"
                  % (len(rc.runs), total, time.time() - t0))
        for what, ok in report:
            log.write("%s: %s\n" % ("same" if ok else "DIFFERENT", what))
    sys.stdout.write((out / "p9kgen.log").read_text())
    # bootcode[] is reported but does not fail the run: s9term was linked
    # against an older libc than the shipped libc.a (docs/plan9_boot_plan.md
    # A3), so the boot program cannot be byte-identical to it.
    return 0 if all(ok for w, ok in report
                    if not w.startswith("bootterm.root.c")) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
