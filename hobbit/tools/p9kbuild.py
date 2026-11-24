#!/usr/bin/env python3
"""Build 1st Edition Plan 9 pieces with the release's own tools, on the
reference model (A3, docs/plan9_boot_plan.md).

Every compile, assembly and archive step is the shipped Hobbit binary
(`hobbit/bin/{zc,za,zl,ar,rl}`) run by `tools/p9run.py` on
`sem/hobbit_sem.py`.  This file only lays out the tree, chooses the
commands the release's mkfiles name, runs them (in parallel processes:
one zc run is ~8 million instructions, ~35 s), and records what came out.

Targets
-------
  all      the whole chain in one fresh --build directory, nothing reused:
           tools/p9kgen.py (into BUILD/kgen), then `kernel --kgen
           BUILD/kgen`, then `link --kgen BUILD/kgen --check` on the
           libram.a just made; BUILD/all.log sums each stage
  kernel   sys/src/9/hobbit/mkfile for one CONF (default `term`): every
           object of $OBJ (`zc -w -Dram`, port files `-I. ../port/X.c`,
           `fcall` without -I., fprt0.s through za), raml.s through za,
           then `ar vu libram.a $OBJ` and `rl libram.a` ($RL, /hobbit/mkfile)
  link     the mkfile's `9term` rule: `za raml.s`, `zc -w -Dram
           -DKERNDATE=<kerndate> term.c`, `zc -w -Dram bootterm.root.c`
           (term.c, bootterm.root.c and kerndate from tools/p9kgen.py,
           --kgen DIR), then `zl -o 9term -l -R4 -H1 -T0x80004000
           -E0x80004000 raml.z term.z bootterm.root.z libram.a -lgnot -lg
           -lc` (libram.a from the kernel target, BUILD/libram.a, or
           --libram); the image is checked by p9exec.check_kernel and
           compared with s9term by tools/p9kcmp.py; --check also requires
           the recorded sha256 (NINETERM_SHA256)
  libc     every C source of sys/src/libc/{hobbit,port,9sys} that has a
           member in the shipped hobbit/lib/libc.a, compiled with `zc` in
           its own directory and compared with that member
  archeck  `ar` and `rl` validated against the shipped libc.a: `ar x`
           every member, give each file the date and mode its header
           records, `ar vu` them back in the archive's order, `rl`, and
           compare the result with the shipped file byte for byte

The build happens in a copy of the vendored tree (`--build DIR`/root,
default hobbit/build/p9kbuild; the tree is DIR/<target>/root), never in
tools/plan9-1e.  Each target
writes `DIR/<target>.log`: one line per step with its status, the
instructions retired, the system calls, the wall time, the output's
size and sha256, and what it printed.

What is not the release's tooling, and why
------------------------------------------
* $DEV/$STREAM/$MISC: the mkfile gets them from `rc ../port/mkdevlist`
  (sed|awk) on the config file.  By default they are read from
  `tools/p9kbuild/<conf>.{dev,stream,misc}list`, written by hand from the
  scripts and the config; `--kgen DIR` takes them instead from
  tools/p9kgen.py's `DIR/objlists`, the scripts' own output with the
  release's sed and awk run on the model (identical for term,
  2026-11-23; the log says so).
* devtab.h: `rc ../port/mkdevh $CONFLIST` (mkextract -u | awk).  By
  default a Python transcription of those two scripts (PROVISIONAL);
  `--kgen DIR` (or --devtab-h FILE) takes the one p9kgen made with
  the release's awk and sort (identical to the transcription for the
  shipped CONFLIST).
* init.h (rammain.c includes it): initcode is assembled and linked on the
  model (`za initcode`, `zl -l -s -o init.out -H2 -T0x1020 -R4
  initcode.z`), and by default the text step (`xd -r -1x init.out | sed
  ...`) is a transcription of xd.c and the two sed expressions
  (PROVISIONAL); `--kgen DIR` (or --init-h FILE) takes p9kgen's, made by
  the release's xd and sed (identical; equal to s9term's initcode[]).
* rl's `fexec("/bin/ar", ...)`: rl forks and execs ar to put the table it
  wrote into the archive (rl.c writerl/fexec).  p9run runs the child (a
  copy of the process, to its exits, before the parent's wait), so rl
  runs to its end; `play_rl` fixes the run's clock at the table's date
  and the directory's mode at 0775 so the table's header is
  reproducible.
* dates and modes: ar copies the input file's mtime and mode into each
  member header.  For a reproducible archive the driver sets every input
  to mode 0664 (what every shipped libc.a member records) and mtime
  726010682 (the shipped libc.a's __.SYMDEF date) before ar runs.

    python3 tools/p9kbuild.py all --build B     # p9kgen+kernel+link, ~3 h
    python3 tools/p9kbuild.py kernel            # everything, 8 processes
    python3 tools/p9kgen.py --out K             # ~75 min (mkroot's sed)
    python3 tools/p9kbuild.py kernel --kgen K
    python3 tools/p9kbuild.py link --kgen K --check
    python3 tools/p9kbuild.py kernel --only trap,clock
    python3 tools/p9kbuild.py libc --only frexp,abs --check
    python3 tools/p9kbuild.py archeck
"""

import argparse
import concurrent.futures
import hashlib
import io
import os
import pathlib
import re
import shutil
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
HOBBIT = HERE.parent
REL = HERE / "plan9-1e"
LISTS = HERE / "p9kbuild"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HOBBIT / "sem"))

FIXED_MTIME = 726010682         # shipped libc.a __.SYMDEF header date
FIXED_MODE = 0o664              # every shipped libc.a member's mode
MAX_STEPS = 200_000_000
LINK_STEPS = 2_000_000_000      # zl of 9term: see target_link's log

#: libc/port C files whose libc.a member is built from libc/hobbit's
#: assembler version instead (hobbit/mkfile OFILES), so the zc object
#: is not expected to match the member.
LIBC_ASM_REPLACED = {"port/" + n for n in (
    "memmove", "memset", "strchr", "strcmp", "strcpy", "strlen",
    "strncmp", "strrchr")}


# --------------------------------------------------------------------
# One run of a 1e binary on the model (in a worker process)
# --------------------------------------------------------------------

def run_tool(root, cwd, tool, args, max_steps=MAX_STEPS, clock=None):
    """Run hobbit/bin/<tool> with `args` in `cwd` (a path under root).
    `clock` fixes the times of the files it writes (p9run Kernel.stamp).
    Instructions and system calls include any child it forks."""
    import p9run
    out = io.BytesIO()
    t0 = time.time()
    status, steps, k, _ops = p9run.run(
        str(pathlib.Path(root) / "hobbit" / "bin" / tool), [tool] + args,
        str(root), max_steps, out, cwd=cwd, clock=clock)
    return {"tool": tool, "args": args, "cwd": cwd, "status": status,
            "steps": steps + k.child_steps,
            "syscalls": len(k.trace) + sum(len(c[3]) for c in k.children),
            "seconds": round(time.time() - t0, 1),
            "console": out.getvalue().decode("latin-1")}


def run_many(root, jobs, specs, max_steps):
    """specs: [(key, cwd, tool, args)] -> {key: result}, in parallel."""
    results = {}
    if jobs <= 1 or len(specs) <= 1:
        for key, cwd, tool, args in specs:
            results[key] = run_tool(root, cwd, tool, args, max_steps)
            report(key, results[key])
        return results
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as ex:
        futs = {ex.submit(run_tool, str(root), cwd, tool, args, max_steps): key
                for key, cwd, tool, args in specs}
        for fut in concurrent.futures.as_completed(futs):
            key = futs[fut]
            results[key] = fut.result()
            report(key, results[key])
    return results


def report(key, r):
    print("  %-14s %-10s %11d insns %4d calls %6.1fs  %s"
          % (key, r["tool"], r["steps"], r["syscalls"], r["seconds"],
             r["status"]), flush=True)


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def ok(r):
    return r["status"] == "exits('')"


# --------------------------------------------------------------------
# The tree
# --------------------------------------------------------------------

def stage(build, target):
    """A fresh copy of the vendored release tree at build/target/root (one
    per target, so targets can run at once), with
    /bin/ar (in 1e /bin is a union that includes /$objtype/bin, and rl
    execs "/bin/ar")."""
    root = pathlib.Path(build) / target / "root"
    if root.exists():
        shutil.rmtree(root)
    shutil.copytree(REL, root)
    (root / "bin").mkdir()
    shutil.copy2(root / "hobbit" / "bin" / "ar", root / "bin" / "ar")
    return root


def read_list(path):
    """One object per line (the mk*list scripts' output); '#' comments."""
    names = []
    for line in pathlib.Path(path).read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.extend(line.split())
    return names


def config_section(text, field, n):
    """mkextract's `select` (sys/src/9/port/mkextract): field n of each
    line of section `field` -- the lines after a line matching ^field,
    until the next line not starting with a tab; blank and # lines are
    skipped."""
    out, doprint = [], False
    for line in text.splitlines():
        if line == "" or line.startswith("#"):
            continue
        if doprint and not line.startswith("\t"):
            doprint = False
        if doprint:
            f = line.split()
            out.append(f[n - 1] if len(f) >= n else "")
        if re.match("^" + field, line):
            doprint = True
    return out


def devtab_h(hobbit_dir, conflist):
    """mkdevh (sys/src/9/port/mkdevh): `mkextract -u dev 1 $CONFLIST |
    awk '{ print the 13 prototypes }'`.  `sort -u` is byte order."""
    names = []
    for conf in conflist:
        names += config_section((hobbit_dir / conf).read_text(), "dev", 1)
    lines = []
    for d in sorted(set(names), key=lambda s: s.encode()):
        lines += ["void\t " + d + "reset(void);",
                  "void\t " + d + "init(void);",
                  "Chan\t*" + d + "attach(char*);",
                  "Chan\t*" + d + "clone(Chan*, Chan*);",
                  "int\t " + d + "walk(Chan*, char*);",
                  "void\t " + d + "stat(Chan*, char*);",
                  "Chan\t*" + d + "open(Chan*, int);",
                  "void\t " + d + "create(Chan*, char*, int, ulong);",
                  "void\t " + d + "close(Chan*);",
                  "long\t " + d + "read(Chan*, void*, long, ulong);",
                  "long\t " + d + "write(Chan*, void*, long, ulong);",
                  "void\t " + d + "remove(Chan*);",
                  "void\t " + d + "wstat(Chan*, char*);"]
    return "\n".join(lines) + "\n"


def xd_r_1x_sed(data):
    """`xd -r -1x FILE | sed -e 's/^[0-9a-f]+ //' -e 's/ ([0-9a-f][0-9a-f])/0x\\1,/g'`,
    transcribed from sys/src/cmd/xd.c: lines of 16 bytes, each byte
    " %.2ux"; -r prints "*" for a 16-byte line equal to the one before;
    at the end (a short read, including a read of 0) the data line is
    printed, then the final address alone."""
    lines, addr, prev, star = [], 0, None, False
    pos = 0
    while True:
        chunk = data[pos:pos + 16]
        pos += len(chunk)
        n = len(chunk)
        if n == 16:
            if addr > 0 and chunk == prev:
                addr += 16
                if not star:
                    star = True
                    lines.append("*")
                continue
            prev, star = chunk, False
        lines.append("%07x " % addr + "".join(" %02x" % b for b in chunk))
        addr += n
        if n < 16:
            lines.append("%07x " % addr)
            break
    out = []
    for ln in lines:
        ln = re.sub(r"^[0-9a-f]+ ", "", ln, count=1)
        ln = re.sub(r" ([0-9a-f][0-9a-f])", r"0x\1,", ln)
        out.append(ln)
    return out


# --------------------------------------------------------------------
# The kernel library
# --------------------------------------------------------------------

#: sys/src/9/hobbit/mkfile OBJ, with ${TYPE}main = rammain and the three
#: lists spliced in where the mkfile has them.
OBJ_HEAD = ["trap", "alarm", "alloc", "chan", "clock", "dev", "fault",
            "latin1", "taslock", "segment", "swap", "rammain", "mmu", "net",
            "page", "pgrp", "print", "proc", "qlock", "queue", "sysfile",
            "sysproc"]
OBJ_TAIL = ["stream", "fcall", "fprt0", "fpihobbit", "fpi"]
CONFLIST = ["cpu", "term", "termlocal", "bart", "rom"]
CFLAGS = ["-w", "-Dram"]


def kgen_lists(kgen):
    """The DEV/STREAM/MISC lines tools/p9kgen.py writes to `objlists`
    (the output of rc ../port/mk{dev,stream,misc}list, run on the
    model) as {"dev": [...], "stream": [...], "misc": [...]}."""
    out = {}
    for line in (pathlib.Path(kgen) / "objlists").read_text().splitlines():
        var, words = line.split("=", 1)
        out[var.lower()] = words.split()
    return out


def kernel_objects(conf, lists=None):
    """$OBJ; `lists` (kgen_lists) replaces the hand-written lists."""
    def lst(kind):
        names = (lists[kind] if lists is not None else
                 read_list(LISTS / ("%s.%slist" % (conf, kind))))
        return [n[:-2] if n.endswith(".z") else n for n in names]
    return OBJ_HEAD + lst("dev") + lst("misc") + lst("stream") + OBJ_TAIL


def kernel_command(name, hobbit_dir, port_dir):
    """The rule portmkfile/mkfile apply to `name`.z."""
    pfiles = {p.stem for p in port_dir.glob("*.c")} - {"fcall"}
    local_c = (hobbit_dir / (name + ".c")).exists()
    if name in pfiles and local_c:
        raise SystemExit("p9kbuild: %s.c is in both port and hobbit" % name)
    if name in pfiles:                      # ^($PFILES)\.$O:R:
        return "zc", CFLAGS + ["-I.", "../port/%s.c" % name]
    if name == "fcall":                     # fcall.$O: ../port/fcall.c
        return "zc", CFLAGS + ["../port/fcall.c"]
    if (hobbit_dir / (name + ".s")).exists():   # %.$O: %.s
        return "za", [name + ".s"]
    if local_c:                             # %.$O: %.c
        return "zc", CFLAGS + [name + ".c"]
    raise SystemExit("p9kbuild: no source for %s.z" % name)


#: every Log opened in this process (target_all sums their steps)
LOGS = []


class Log:
    def __init__(self, path):
        self.path = path
        self.f = open(path, "w")
        self.steps = 0          # instructions of every step logged
        self.runs = 0
        LOGS.append(self)

    def line(self, key, r, out=None, note=""):
        self.steps += r["steps"]
        self.runs += 1
        size = digest = "-"
        if out is not None and pathlib.Path(out).exists():
            size = str(pathlib.Path(out).stat().st_size)
            digest = sha(out)
        self.f.write("\t".join([key, r["tool"] + " " + " ".join(r["args"]),
                                r["status"], str(r["steps"]),
                                str(r["syscalls"]), str(r["seconds"]), size,
                                digest, note,
                                r["console"].replace("\n", "\\n")]) + "\n")
        self.f.flush()

    def note(self, text):
        self.f.write("# " + text + "\n")
        self.f.flush()


def play_rl(root, cwd, libname, log, max_steps, mtime=FIXED_MTIME,
            mode=FIXED_MODE):
    """$RL $LIBRARY: run rl on `libname` to its end.  rl.c writerl()
    creates __.SYMDEF (perm 0664), writes the table, then fexec()s
    `/bin/ar rb|mb|r ...` (fork, exec, wait: p9run runs the child) and
    removes __.SYMDEF.  ar copies the table file's date and mode into its
    member header, so the run's clock is fixed at `mtime` and the
    directory is given mode 0775 (create's perm is ANDed with the
    directory's, open(2)), which leaves 0664 = `mode`."""
    import build_zl_inferno
    d = pathlib.Path(root) / cwd
    if mode != 0o664:
        raise SystemExit("p9kbuild: rl creates __.SYMDEF 0664, not %o"
                         % mode)
    os.chmod(d, 0o775)
    r = run_tool(root, cwd, "rl", [libname], max_steps, clock=mtime)
    report("rl", r)
    log.line("rl", r, d / libname, "rl's fork+exec of ar run by p9run")
    if not ok(r):
        raise SystemExit("p9kbuild: rl failed: %s" % r["status"])
    members = list(build_zl_inferno.read_members(str(d / libname)))
    if members[:1] != ["__.SYMDEF"] or (d / "__.SYMDEF").exists():
        raise SystemExit("p9kbuild: rl exited but left no table first")
    hdr = (d / libname).read_bytes()[8:68]
    if (int(hdr[16:28].decode().strip()) != mtime
            or int(hdr[40:48].decode().strip(), 8) != mode):
        raise SystemExit("p9kbuild: __.SYMDEF header %r: not dated %d "
                         "mode %o" % (hdr, mtime, mode))


def make_library(root, cwd, libname, names, log, max_steps):
    """$LIBRARY: `ar vu $LIBRARY $names; $RL $LIBRARY` (mkfile)."""
    d = pathlib.Path(root) / cwd
    for n in names:
        os.chmod(d / n, FIXED_MODE)
        os.utime(d / n, (FIXED_MTIME, FIXED_MTIME))
    lib = d / libname
    if lib.exists():
        lib.unlink()
    r = run_tool(root, cwd, "ar", ["vu", libname] + names, max_steps)
    report("ar vu", r)
    log.line("ar vu", r, lib)
    if not ok(r):
        raise SystemExit("p9kbuild: ar vu failed: %s" % r["status"])
    play_rl(root, cwd, libname, log, max_steps)
    return lib


def target_kernel(a):
    build = pathlib.Path(a.build)
    build.mkdir(parents=True, exist_ok=True)
    root = stage(build, "kernel-" + a.conf)
    cwd = "sys/src/9/hobbit"
    hdir, pdir = root / cwd, root / "sys/src/9/port"
    log = Log(build / ("kernel-%s.log" % a.conf))
    log.note("p9kbuild kernel CONF=%s; columns: object, command, status, "
             "instructions, syscalls, seconds, size, sha256, note, console"
             % a.conf)

    provisional = set()
    lists = None
    if a.kgen:
        # tools/p9kgen.py's products: rc's scripts run on the model
        kg = pathlib.Path(a.kgen)
        a.devtab_h = a.devtab_h or str(kg / "devtab.h")
        a.init_h = a.init_h or str(kg / "init.h")
        lists = kgen_lists(kg)
        for kind in ("dev", "stream", "misc"):
            hand = read_list(LISTS / ("%s.%slist" % (a.conf, kind)))
            log.note("%slist from %s: %s the hand list (%d objects)"
                     % (kind, kg, "same as" if hand == lists[kind]
                        else "DIFFERENT from", len(lists[kind])))
        tdevtab = devtab_h(hdir, CONFLIST)
        log.note("devtab.h from %s: %s the transcription" % (
            kg, "same as" if (kg / "devtab.h").read_text() == tdevtab
            else "DIFFERENT from"))
    if a.devtab_h:
        shutil.copy(a.devtab_h, hdir / "devtab.h")
        log.note("devtab.h from %s" % a.devtab_h)
    else:
        (hdir / "devtab.h").write_text(devtab_h(hdir, CONFLIST))
        log.note("devtab.h PROVISIONAL: mkdevh transcribed in Python, "
                 "sha256 %s" % sha(hdir / "devtab.h"))
    objs = kernel_objects(a.conf, lists)
    only = set(a.only.split(",")) if a.only else None
    want = [o for o in objs if only is None or o in only]
    if only and only - set(objs) - {"raml"}:
        raise SystemExit("p9kbuild: not in $OBJ: %s"
                         % ", ".join(sorted(only - set(objs) - {"raml"})))

    if "rammain" in want:
        if a.init_h:
            shutil.copy(a.init_h, hdir / "init.h")
            log.note("init.h from %s" % a.init_h)
        else:
            for key, tool, args in [
                    ("initcode", "za", ["initcode"]),
                    ("init.out", "zl", ["-l", "-s", "-o", "init.out", "-H2",
                                        "-T0x1020", "-R4", "initcode.z"])]:
                r = run_tool(root, cwd, tool, args, a.max_steps)
                report(key, r)
                log.line(key, r, hdir / ("initcode.z" if tool == "za"
                                         else "init.out"))
                if not ok(r):
                    raise SystemExit("p9kbuild: %s failed" % key)
            body = xd_r_1x_sed((hdir / "init.out").read_bytes())
            (hdir / "init.h").write_text(
                "uchar initcode[]={\n" + "\n".join(body) + "\n};\n")
            provisional.add("rammain")
            log.note("init.h PROVISIONAL: xd|sed transcribed, sha256 %s"
                     % sha(hdir / "init.h"))

    specs = []
    for o in want:
        tool, args = kernel_command(o, hdir, pdir)
        specs.append((o, cwd, tool, args))
    if only is None or "raml" in only:
        specs.append(("raml", cwd, "za", ["raml.s"]))
    t0 = time.time()
    print("p9kbuild: %d steps, %d processes" % (len(specs), a.jobs))
    res = run_many(root, a.jobs, specs, a.max_steps)
    failed = []
    total = 0
    for key, _cwd, _t, _a in specs:
        r = res[key]
        total += r["steps"]
        out = hdir / (key + ".z")
        log.line(key, r, out,
                 "PROVISIONAL (init.h)" if key in provisional else "")
        if not ok(r) or not out.exists():
            failed.append(key)
    log.note("compiled %d of %d, %d instructions, %.0f s wall"
             % (len(specs) - len(failed), len(specs), total,
                time.time() - t0))
    print("p9kbuild: %d of %d built, %d instructions, %.0f s"
          % (len(specs) - len(failed), len(specs), total, time.time() - t0))
    if failed:
        print("p9kbuild: FAILED: " + " ".join(failed))
        return 1
    if only is None and not a.no_library:
        lib = make_library(root, cwd, "libram.a", [o + ".z" for o in objs],
                           log, a.max_steps)
        log.note("libram.a %d bytes sha256 %s"
                 % (lib.stat().st_size, sha(lib)))
        print("p9kbuild: libram.a %d bytes sha256 %s"
              % (lib.stat().st_size, sha(lib)))
        shutil.copy2(lib, build / "libram.a")
    return 0


# --------------------------------------------------------------------
# The link: 9$CONF
# --------------------------------------------------------------------

#: The sha256 of libram.a for `term` as the kernel target makes it
#: (docs/plan9_boot_plan.md A3).  Reported by `all`, not enforced here:
#: its __.SYMDEF carries rl's stack residue (target_archeck).
LIBRAM_SHA256 = ("f709cea932f1a3694a08a93f4eb013c4"
                 "a0703499938d0a9cd31ba0d8515b7ea6")
#: sys/src/9/hobbit/mkfile, rule `9term 9bart 9termlocal`.
LINK_FLAGS = ["-l", "-R4", "-H1", "-T0x80004000", "-E0x80004000"]
LINK_LIBS = ["-lgnot", "-lg", "-lc"]
#: The sha256 of `9term` as the recorded command makes it from the
#: generated inputs of tools/p9kgen.py and libram.a f709cea9...
#: (docs/plan9_boot_plan.md A3).  `link --check` fails on any other.
NINETERM_SHA256 = ("002880c011bd7418c36c036b16f450e6"
                   "1d1ed43e1ec963a6f5b4574a2eece1b1")


#: sizeof(struct mipsexec) (sys/include/bootexec.h): libmach's hdrsz for
#: a "hobbit plan 9 boot image" (executable.c exectab), which size.c
#: subtracts from a txtsz that, for that format, never included it.
MIPSEXEC_SIZE = 76


def size_line(k, name):
    """What the release's `size NAME` prints for the -H1 image k
    (p9exec.read_kernel): size.c's "%ldt + %ldd + %ldb = %ld\t%s\n" of
    crackhdr()'s txtsz - hdrsz, datsz, bsssz; hobbitboot() sets txtsz =
    the header's text, so the text figure is 76 short of it."""
    text = k["text"] - MIPSEXEC_SIZE
    return "%dt + %dd + %db = %d\t%s\n" % (
        text, k["data"], k["bss"], text + k["data"] + k["bss"], name)


def target_link(a):
    """9$CONF: the mkfile's rule, with its three inputs made on the model:
        $CC $CFLAGS '-DKERNDATE='`{date -n} $CONF.c
        $LD -o $target -l -R4 -H1 -T0x80004000 -E0x80004000 \\
            ${TYPE}l.$O $CONF.$O boot$CONF.root.$O lib$TYPE.a $LIB
    ($LIB = -lgnot -lg -lc).  raml.s is assembled and boot$CONF.root.c
    compiled here too (portmkfile's %.$O rules), so the link's inputs
    are: tools/p9kgen.py's $CONF.c, boot$CONF.root.c and kerndate
    (--kgen DIR), and libram.a (--libram, default BUILD/libram.a, the
    `kernel` target's product).  The rule's last command, `size 9$CONF`,
    is run too (size_line: its line must be the header's figures)."""
    if not a.kgen:
        raise SystemExit("p9kbuild: link needs --kgen DIR (tools/p9kgen.py)")
    kg = pathlib.Path(a.kgen)
    build = pathlib.Path(a.build)
    build.mkdir(parents=True, exist_ok=True)
    libram = pathlib.Path(a.libram or build / "libram.a")
    if not libram.exists():
        raise SystemExit("p9kbuild: no %s (run the kernel target first, or "
                         "give --libram)" % libram)
    conf = a.conf
    target = "9" + conf
    root = stage(build, "link-" + conf)
    cwd = "sys/src/9/hobbit"
    hdir = root / cwd
    log = Log(build / ("link-%s.log" % conf))
    log.note("p9kbuild link CONF=%s; columns: step, command, status, "
             "instructions, syscalls, seconds, size, sha256, note, console"
             % conf)
    kerndate = int((kg / "kerndate").read_text().split()[0])
    for name in (conf + ".c", "boot%s.root.c" % conf, "devtab.h", "init.h"):
        shutil.copy(kg / name, hdir / name)
        log.note("input %s from %s sha256 %s" % (name, kg, sha(hdir / name)))
    shutil.copy(libram, hdir / "libram.a")
    log.note("input libram.a from %s sha256 %s"
             % (libram, sha(hdir / "libram.a")))
    for lib in ("libgnot.a", "libg.a", "libc.a"):
        log.note("input /hobbit/lib/%s (vendored) sha256 %s"
                 % (lib, sha(root / "hobbit/lib" / lib)))
    log.note("KERNDATE %d from %s/kerndate" % (kerndate, kg))
    specs = [("raml", cwd, "za", ["raml.s"]),
             (conf, cwd, "zc", CFLAGS + ["-DKERNDATE=%d" % kerndate,
                                         conf + ".c"]),
             ("boot%s.root" % conf, cwd, "zc",
              CFLAGS + ["boot%s.root.c" % conf])]
    t0 = time.time()
    res = run_many(root, a.jobs, specs, a.max_steps)
    for key, _c, _t, _a in specs:
        log.line(key, res[key], hdir / (key + ".z"))
        if not ok(res[key]) or not (hdir / (key + ".z")).exists():
            raise SystemExit("p9kbuild: %s failed: %s"
                             % (key, res[key]["status"]))
    for key in ("raml", conf, "boot%s.root" % conf):
        theirs = kg / (key + ".z")
        if theirs.exists():
            log.note("%s.z %s the one in %s" % (
                key, "same as" if theirs.read_bytes() ==
                (hdir / (key + ".z")).read_bytes() else "DIFFERENT from",
                kg))
    args = (["-o", target] + LINK_FLAGS +
            ["raml.z", conf + ".z", "boot%s.root.z" % conf, "libram.a"] +
            LINK_LIBS)
    r = run_tool(root, cwd, "zl", args, a.link_steps)
    report("zl", r)
    out = hdir / target
    log.line("zl", r, out)
    if not ok(r) or not out.exists() or r["console"]:
        raise SystemExit("p9kbuild: zl: %s %r" % (r["status"], r["console"]))
    shutil.copy2(out, build / target)
    digest = sha(out)
    msg = ("%s %d bytes sha256 %s; zl %d instructions, %.0f s; %.0f s in all"
           % (target, out.stat().st_size, digest, r["steps"], r["seconds"],
              time.time() - t0))
    log.note(msg)
    print("p9kbuild: " + msg)
    import p9exec
    import p9kcmp
    k = p9exec.read_kernel(str(out))
    r = run_tool(root, cwd, "size", [target], a.max_steps)
    report("size", r)
    want = size_line(k, target)
    log.line("size", r, None, "header's figures" if r["console"] == want
             else "NOT the header's figures: %r" % want)
    print("p9kbuild: " + r["console"].rstrip("\n"))
    if not ok(r) or r["console"] != want:
        print("p9kbuild: FAILED: size printed %r, the header says %r"
              % (r["console"], want))
        return 1
    problems = p9exec.check_kernel(k, p9exec.kernel_symbols(k))
    log.note("p9exec.check_kernel: %s" % ("; ".join(problems) or "passes"))
    status = p9kcmp.compare(p9kcmp.Image(out), p9kcmp.Image(p9kcmp.S9TERM))
    log.note("p9kcmp against s9term: exit %d" % status)
    if problems or status:
        return 1
    if a.check and conf == "term":
        if digest != NINETERM_SHA256:
            print("p9kbuild: FAILED: %s sha256 %s, recorded %s"
                  % (target, digest, NINETERM_SHA256))
            return 1
        print("p9kbuild: %s is the recorded image" % target)
    return 0


# --------------------------------------------------------------------
# libc: the compiler against the shipped archive
# --------------------------------------------------------------------

def libc_sources(members):
    out = []
    for sub in ("hobbit", "port", "9sys"):
        for c in sorted((REL / "sys/src/libc" / sub).glob("*.c")):
            if c.stem + ".z" in members:
                out.append(sub + "/" + c.stem)
    return out


def target_libc(a):
    import build_zl_inferno
    members = build_zl_inferno.read_members(str(REL / "hobbit/lib/libc.a"))
    srcs = libc_sources(members)
    if a.only:
        only = a.only.split(",")
        srcs = [s for s in srcs if s in only or s.split("/")[1] in only]
        unmatched = [o for o in only
                     if not any(o in (s, s.split("/")[1]) for s in srcs)]
        if unmatched:
            raise SystemExit("p9kbuild: no libc source with a libc.a member "
                             "matches %s" % ", ".join(unmatched))
    build = pathlib.Path(a.build)
    build.mkdir(parents=True, exist_ok=True)
    root = stage(build, "libc")
    log = Log(build / "libc.log")
    log.note("p9kbuild libc: zc FILE.c in sys/src/libc/DIR, compared with "
             "the shipped libc.a member")
    specs = [(s, "sys/src/libc/" + s.split("/")[0], "zc",
              [s.split("/")[1] + ".c"]) for s in srcs]
    t0 = time.time()
    print("p9kbuild: %d files, %d processes" % (len(specs), a.jobs))
    res = run_many(root, a.jobs, specs, a.max_steps)
    same, differ, failed, total = [], [], [], 0
    for s in srcs:
        r = res[s]
        total += r["steps"]
        out = root / "sys/src/libc" / (s + ".z")
        if not ok(r) or not out.exists():
            failed.append(s)
            log.line(s, r, out, "FAILED")
            continue
        match = out.read_bytes() == members[out.name]
        (same if match else differ).append(s)
        note = "identical to the libc.a member" if match else (
            "differs: the member is libc/hobbit's assembler version"
            if s in LIBC_ASM_REPLACED else "DIFFERS")
        log.line(s, r, out, note)
    unexpected = [s for s in differ if s not in LIBC_ASM_REPLACED]
    summary = ("%d files: %d identical, %d differ (%d expected: assembler "
               "members), %d failed; %d instructions, %.0f s"
               % (len(srcs), len(same), len(differ),
                  len(differ) - len(unexpected), len(failed), total,
                  time.time() - t0))
    log.note(summary)
    print("p9kbuild: " + summary)
    if failed or (a.check and unexpected):
        print("p9kbuild: FAILED: " + " ".join(failed + unexpected))
        return 1
    return 0


# --------------------------------------------------------------------
# archeck: ar and rl against the shipped libc.a
# --------------------------------------------------------------------

def ar_headers(data):
    """[(name, header bytes, body bytes)] of an ar archive."""
    out, off = [], 8
    while off + 60 <= len(data):
        hdr = data[off:off + 60]
        size = int(hdr[48:58].decode().strip())
        out.append((hdr[0:16].decode("latin-1").rstrip(), hdr,
                    data[off + 60:off + 60 + size]))
        off += 60 + size + (size & 1)
    return out


def target_archeck(a):
    build = pathlib.Path(a.build)
    build.mkdir(parents=True, exist_ok=True)
    root = stage(build, "archeck")
    cwd = "archeck"
    d = root / cwd
    d.mkdir()
    shipped = (REL / "hobbit/lib/libc.a").read_bytes()
    shutil.copy(REL / "hobbit/lib/libc.a", d / "libc.a")
    log = Log(build / "archeck.log")
    entries = ar_headers(shipped)
    names = [n for n, _h, _b in entries if n != "__.SYMDEF"]
    if a.only:
        names = [n for n in names if n[:-2] in a.only.split(",")]
    # 1. ar t lists the members
    r = run_tool(root, cwd, "ar", ["t", "libc.a"], a.max_steps)
    report("ar t", r)
    log.line("ar t", r)
    listed = r["console"].split()
    if not ok(r) or listed != [n for n, _h, _b in entries]:
        raise SystemExit("p9kbuild: ar t does not list libc.a's members")
    # 2. ar x extracts each member's bytes
    r = run_tool(root, cwd, "ar", ["x", "libc.a"] + names, a.max_steps)
    report("ar x", r)
    log.line("ar x", r)
    body = {n: b for n, _h, b in entries}
    bad = [n for n in names if (d / n).read_bytes() != body[n]]
    if not ok(r) or bad:
        raise SystemExit("p9kbuild: ar x: %s" % (bad or r["status"]))
    # 3. ar vu + rl rebuild it from them, dated and moded as the headers say
    hdr = {n: h for n, h, _b in entries}
    for n in names:
        os.chmod(d / n, int(hdr[n][40:48].decode().strip(), 8))
        t = int(hdr[n][16:28].decode().strip())
        os.utime(d / n, (t, t))
    r = run_tool(root, cwd, "ar", ["vu", "new.a"] + names, a.max_steps)
    report("ar vu", r)
    log.line("ar vu", r, d / "new.a")
    if not ok(r):
        raise SystemExit("p9kbuild: ar vu: %s" % r["status"])
    play_rl(root, cwd, "new.a", log, a.max_steps,
            mtime=int(hdr["__.SYMDEF"][16:28].decode().strip()),
            mode=int(hdr["__.SYMDEF"][40:48].decode().strip(), 8))
    made = (d / "new.a").read_bytes()
    if a.only:
        print("p9kbuild: subset: new.a %d bytes (not compared whole)"
              % len(made))
        return 0
    same = made == shipped
    msg = ("rebuilt libc.a %s the shipped one (%d bytes, sha256 %s)"
           % ("IS byte-identical to" if same else "DIFFERS from",
              len(made), hashlib.sha256(made).hexdigest()))
    verdict = same
    if not same:
        verdict, detail = symdef_residue_only(ar_headers(made), entries)
        msg += "; " + detail
    log.note(msg)
    print("p9kbuild: " + msg)
    return 0 if verdict else 1


RLENTSIZE = 4 + 20 + 4          # rl.c: offset, NNAME (a.out.h) name, type


def symdef_entries(body):
    """rl.c writerl(): (offset, name up to its NUL, type byte, padding)."""
    out = []
    for i in range(0, len(body), RLENTSIZE):
        e = body[i:i + RLENTSIZE]
        out.append((e[0:4], e[4:24].split(b"\0")[0], e[24:28]))
    return out


def symdef_residue_only(got, want):
    """True when two archives differ only in the bytes after the NUL of
    __.SYMDEF name fields.  rl writes NNAME bytes from each Sym name, and
    those come from libmach obj.c readar()'s local `Prog p`, whose id[]
    is filled only up to the NUL: past it is whatever the stack held,
    which is not a property of rl, ar or the archive."""
    if len(got) != len(want):
        return False, "member count %d vs %d" % (len(got), len(want))
    for i, (g, w) in enumerate(zip(got, want)):
        if g == w:
            continue
        if g[0] != "__.SYMDEF" or w[0] != "__.SYMDEF" or g[1] != w[1]:
            return False, "first difference at member %d (%s vs %s)" % (
                i, g[0], w[0])
        if symdef_entries(g[2]) != symdef_entries(w[2]):
            return False, "__.SYMDEF entries differ (offset, name or type)"
        nbytes = sum(a != b for a, b in zip(g[2], w[2]))
        n = len(g[2]) // RLENTSIZE
        detail = ("every member and header identical; __.SYMDEF's %d "
                  "entries identical in offset, name and type, %d bytes "
                  "differ, all after a name's NUL (readar's uninitialised "
                  "Prog.id)" % (n, nbytes))
        try:
            import p9symdef
            full = b"!<arch>\n" + b"".join(
                h + b + b"\n" * (len(b) & 1) for _n, h, b in want)
            c, odd = p9symdef.explain(full)
            mine, _odd = p9symdef.explain(full, g[2])
            detail += ("; of the shipped table's %d bytes past the NULs, "
                       "%d are in-call bytes as replayed and %d stack bytes "
                       "as /mips/bin/rl's frames leave them; %d are not"
                       "; this table's: %d in-call as replayed, %d stack "
                       "bytes the MIPS frames would differ in -- the "
                       "Hobbit rl's own (tools/p9symdef.py)"
                       % (c["in_call"] + c["pre"], c["in_call_same"],
                          c["pre_mips"], len(odd), mine["in_call_same"],
                          mine["pre"] - mine["pre_mips"]))
        except SystemExit as exc:
            detail += "; p9symdef: %s" % exc
    return True, detail


# --------------------------------------------------------------------
# all: the whole chain from the vendored tree
# --------------------------------------------------------------------

def target_all(a):
    """p9kgen, then `kernel --kgen`, then `link --kgen --check`, in one
    fresh build directory: BUILD/kgen (tools/p9kgen.py's products and
    log), BUILD/kernel-CONF{,.log}, BUILD/link-CONF{,.log}; nothing is
    taken from an earlier run.  BUILD/all.log records each stage's
    programs, instructions and wall time, and the products' sha256."""
    import p9kgen
    build = pathlib.Path(a.build)
    if build.exists() and any(build.iterdir()):
        raise SystemExit("p9kbuild: all wants a fresh --build directory; "
                         "%s is not empty" % build)
    build.mkdir(parents=True, exist_ok=True)
    kg = build / "kgen"
    kg.mkdir()
    summary = open(build / "all.log", "w")

    def note(text):
        print("p9kbuild all: " + text, flush=True)
        summary.write(text + "\n")
        summary.flush()

    t_all = time.time()
    stages = []
    t0 = time.time()
    with open(kg / "p9kgen.log", "w") as klog:
        products, rc = p9kgen.generate(kg, a.conf, True, klog)
        report = p9kgen.check(products, a.conf)
        for what, good in report:
            klog.write("%s: %s\n" % ("same" if good else "DIFFERENT", what))
    ksteps = sum(r[2] for r in rc.runs)
    stages.append(("p9kgen", len(rc.runs), ksteps, time.time() - t0))
    note("p9kgen: %d programs, %d instructions, %.0f s"
         % stages[-1][1:])
    for what, good in report:
        note("  %s: %s" % ("same" if good else "DIFFERENT", what))
    if not all(good for what, good in report
               if not what.startswith("bootterm.root.c")):
        note("FAILED: p9kgen's checks")
        return 1
    a.kgen = str(kg)
    for name, fn in (("kernel", target_kernel), ("link", target_link)):
        if name == "link":
            a.libram = str(build / "libram.a")
            a.check = True
        t0 = time.time()
        n0 = len(LOGS)
        status = fn(a)
        logs = LOGS[n0:]
        stages.append((name, sum(lg.runs for lg in logs),
                       sum(lg.steps for lg in logs), time.time() - t0))
        note("%s: %d programs, %d instructions, %.0f s" % stages[-1])
        if status:
            note("FAILED: %s exited %d" % (name, status))
            return status
    lib = build / "libram.a"
    img = build / ("9" + a.conf)
    note("libram.a %d bytes sha256 %s (%s LIBRAM_SHA256)"
         % (lib.stat().st_size, sha(lib),
            "=" if sha(lib) == LIBRAM_SHA256 else "DIFFERENT from"))
    note("%s %d bytes sha256 %s%s" % (
        img.name, img.stat().st_size, sha(img),
        " (= NINETERM_SHA256, link --check passed)"
        if a.conf == "term" else ""))
    note("total: %d programs, %d instructions, %.0f s wall"
         % (sum(s[1] for s in stages), sum(s[2] for s in stages),
            time.time() - t_all))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", choices=["all", "kernel", "link", "libc",
                                       "archeck"])
    ap.add_argument("--build", default=str(HOBBIT / "build" / "p9kbuild"),
                    help="build directory (each target's staged tree is "
                    "BUILD/<target>/root)")
    ap.add_argument("--conf", default="term")
    ap.add_argument("--only", help="comma-separated subset (object stems)")
    ap.add_argument("-j", "--jobs", type=int, default=8)
    ap.add_argument("--max-steps", type=int, default=MAX_STEPS)
    ap.add_argument("--check", action="store_true",
                    help="libc: fail if any object differs unexpectedly; "
                    "link: fail unless 9term has the recorded sha256")
    ap.add_argument("--libram", help="link: the libram.a to link "
                    "(default BUILD/libram.a, the kernel target's)")
    ap.add_argument("--link-steps", type=int, default=LINK_STEPS,
                    help="link: zl's instruction limit")
    ap.add_argument("--devtab-h", help="use this devtab.h, not the "
                    "transcribed mkdevh")
    ap.add_argument("--init-h", help="use this init.h, not the "
                    "provisional one")
    ap.add_argument("--kgen", metavar="DIR",
                    help="kernel: take devtab.h, init.h and the DEV/STREAM/"
                    "MISC lists from a tools/p9kgen.py output directory")
    ap.add_argument("--no-library", action="store_true",
                    help="kernel: compile only; no ar/rl")
    a = ap.parse_args(argv)
    return {"all": target_all, "kernel": target_kernel, "link": target_link,
            "libc": target_libc, "archeck": target_archeck}[a.target](a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
