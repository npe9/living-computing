#!/usr/bin/env python3
"""Build the 1st Edition Plan 9 `z` linker (zl) on this host, with Inferno.

The owner's route: use the Inferno64 tree's C environment (lib9/libbio
headers and libraries, built by its own makemk.sh), not plan9port.  The
linker is Plan 9 C from 1993, so a handful of edits are unavoidable;
every one is listed here so the build is reproducible and auditable:

  * `<u.h>` / `<libc.h>` become shims to Inferno's `<lib9.h>`;
  * `Ieee` comes from `zc/z.out.h` (it is defined there), not <ieee.h>;
  * `ar_hdr.name` / `.size` / `.fmag` are the host BSD ar members;
  * the linker's own `malloc/calloc/realloc/free` are renamed: Inferno's
    lib9.h maps those names to `k*` allocators by macro;
  * `cputime` is renamed and returns milliseconds: Inferno's fmt has no
    floating conversions at all (`lib9/dofmt.c` has no `%f`), so the
    vendored `%5.2f` timing formats become `%5ld` and every `%P` (the
    1e-installed program conversion) is dropped -- Inferno's fmt would
    otherwise hand the installed conversion its own `va_list`, which
    the 1993 `Fconv` protocol does not match, and the program dump
    dereferenced rubbish;
  * `strconv`, `doprint` and `argv0` are supplied (Inferno's lib9 has no
    1st Edition `strconv`/`doprint`); `strconv` is the 1993 fmt
    callback, not a number parser, so the installed `%A/%D/%P`
    conversions are not installed (`listinit` is empty here) and the
    listings print parcel words instead of symbolic instructions;
  * `Rlent.offset` is a 32-bit `int`: the 1e symbol table entry is
    28 bytes and a host `long` would make it 32, which is what made the
    shipped archives read as "bad or out of date";
  * the library directory (`/hobbit/lib`) is taken from `$ZLLIB`, so
    the auto-library records inside `libc.a` members find the vendored
    archive instead of a path that does not exist on this host;
  * `diag`'s 1993 varargs hack `&(&a)[1]` becomes `va_start`/`va_end`.
    That hack passes a pointer into the caller's stack frame as a
    `va_list`; on arm64 the callee then reads the bytes of the format
    string ("undefine...") as the `%s` argument, which was the
    `EXC_BAD_ACCESS` in `strlen`.
  * `ldobj` zeroes each `Prog` it allocates.  `AHISTORY` records carry
    `D_NONE` operands, and `zaddr` does not set `offset` for `D_NONE`,
    so the 1993 code reads uninitialised `hunk` for `to.offset`; a
    non-zero value there is read as "this object came from library N"
    and sends `loadlib` to a path that does not exist.

Nothing in the repository's vendored sources is edited: the script
copies them into a build directory and patches the copies.  Every patch
below is asserted, so a changed vendored source fails loudly instead of
silently skipping an edit.

    python3 tools/build_zl_inferno.py [--root ~/src/inferno64] [--out DIR]
    python3 tools/build_zl_inferno.py --link-main9 [--libc PATH]

`--link-main9` additionally links Bell Labs' own `main9.z` (from the
release's `libc.a`) with the real members that define `_clock` and
`exits`, and prints the header and `_main`'s parcels.  A program object
is supplied because `main` is the program's symbol and a library cannot
define it; it is one `RETURN`, and it is linked first so that `main`
lands at the text base 0x1020 as it does in `cat` and `echo`.
"""

import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "plan9-1e", "sys", "src", "cmd")
DEFAULT_LIBC = os.path.join(HERE, "plan9-1e", "hobbit", "lib", "libc.a")

# (file, old, new) -- applied to copies under <out>/zl.  Each `old` must
# occur exactly once, else the build stops.
PATCHES = [
    # ---------------------------------------------------------------- l.h
    ("l.h",
     '#include "../zc/z.out.h"\n',
     '#include "../zc/z.out.h"\n'
     '/* Host port: the 1993 fmt callbacks and the host replacements. */\n'
     'typedef void (*Fconv)();\n'
     'char* zllibdir(void);\n'
     'long zlcputime(void);\n'
     'char* doprint(char*, char*, char*, va_list);\n'
     '/* Host port: the 1993 fmt callback, refused loudly if ever called */\n'
     'void strconv(char*, void*);\n'),
    ("l.h", "double\tcputime(void);", "long\tzlcputime(void);"),

    # --------------------------------------------------------------- obj.c
    ("obj.c", "arhdr.name", "arhdr.ar_name"),
    ("obj.c", "arhdr.size", "arhdr.ar_size", "all"),
    ("obj.c",
     "\t\tif(strncmp(arhdr.fmag, ARFMAG, sizeof(arhdr.fmag)))\n"
     "\t\t\tgoto bad;",
     "#ifndef __APPLE__\n"
     "\t\tif(strncmp(arhdr.fmag, ARFMAG, sizeof(arhdr.fmag)))\n"
     "\t\t\tgoto bad;\n"
     "#endif"),
    # The library directory: /hobbit/lib on the 1993 machine, $ZLLIB here.
    ("obj.c",
     '\t\tif(debug[\'9\'])\n'
     '\t\t\tstrcpy(name, "/hobbit/lib/lib");\n'
     '\t\telse\n'
     '\t\t\tstrcpy(name, "/usr/zlib/lib");\n'
     '\t\tstrcat(name, file+2);',
     '\t\tstrcpy(name, zllibdir());\n'
     '\t\tstrcat(name, "/lib");\n'
     '\t\tstrcat(name, file+2);'),
    ("obj.c",
     '\t\tif(debug[\'9\'])\n'
     '\t\t\tstrcpy(name, "/hobbit/lib");\n'
     '\t\telse\n'
     '\t\t\tstrcpy(name, "/usr/zlib");\n'
     '\t\ti = 0;',
     '\t\tstrcpy(name, zllibdir());\n'
     '\t\ti = 0;'),
    # AHISTORY's D_NONE operands leave to.offset unset; zero the Prog.
    ("obj.c",
     "\tp = (Prog*)hunk;\n"
     "\tnhunk -= sizeof(Prog);\n"
     "\thunk += sizeof(Prog);\n"
     "/*\t*p = zprg; */\n",
     "\tp = (Prog*)hunk;\n"
     "\tnhunk -= sizeof(Prog);\n"
     "\thunk += sizeof(Prog);\n"
     "\tmemset(p, 0, sizeof(Prog));\t/* host port: hunk is not zeroed */\n"),

    # -------------------------------------------------------------- list.c
    # The crash: `&(&a)[1]` is a pointer into the caller's frame, not a
    # va_list.  Use the host's varargs.
    ("list.c",
     "\tdoprint(buf, buf+sizeof(buf), a, &(&a)[1]);\t/* ugly */",
     "\tva_list arg;\n"
     "\n"
     "\tva_start(arg, a);\n"
     "\tdoprint(buf, buf+sizeof(buf), a, arg);\n"
     "\tva_end(arg);"),
    # Do not install the 1993 conversions into the host formatter: it
    # calls them with its own va_list, which the Fconv protocol does not
    # match (that is what crashed on `%P`).
    ("list.c",
     "\tfmtinstall('A', Aconv);\n"
     "\tfmtinstall('D', Dconv);\n"
     "\tfmtinstall('S', Sconv);\n"
     "\tfmtinstall('W', Wconv);\n"
     "\tfmtinstall('P', Pconv);\n",
     "\t/* Host port: no 1e conversions (see the build script). */\n"),
]

RENAMES = [("malloc(", "zlmalloc("), ("calloc(", "zlcalloc("),
           ("realloc(", "zlrealloc("), ("free(", "zlfree("),
           ("cputime(", "zlcputime(")]

# Inferno's fmt has no %f (lib9/dofmt.c) and no installed %P: the
# timing prints become integer milliseconds and the program dump goes.
FMT_FIXES = [("%5.2f", "%5ld"), ("%P", "")]

SHIM_U = "#include <lib9.h>\n"
SHIM_LIBC = "/* lib9.h is pulled in by the u.h shim */\n"
SHIM_C = """\
/* Calls the 1st Edition linker makes that Inferno's lib9 does not have. */
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <time.h>
#include <string.h>

long zlcputime(void) { return (long)(clock() * 1000 / CLOCKS_PER_SEC); }

/* The 1993 `strconv` is the fmt engine's output callback, not a number
 * parser; the host formatter never calls it (listinit installs nothing),
 * so reaching it is a bug and says so. */
void strconv(char *s, void *fp)
{
	(void)s; (void)fp;
	fprintf(stderr, "zl: 1993 strconv is not available on this host\\n");
	abort();
}

char *doprint(char *buf, char *end, char *fmt, va_list a)
{
\tint n = vsnprintf(buf, end - buf, fmt, a);
\tchar *s = buf + (n < 0 ? 0 : n);
\treturn s < end ? s : end - 1;
}

char *argv0;

/* $ZLLIB, or the 1993 path as a loud fallback (the archive records say
 * /hobbit/lib; on this host that normally does not exist). */
char *zllibdir(void)
{
\tstatic char *d = 0;
\tif(d == 0) {
\t\td = getenv("ZLLIB");
\t\tif(d == 0)
\t\t\td = "/hobbit/lib";
\t}
\treturn d;
}
"""


def apply_patches(text, pairs, name):
    for entry in pairs:
        old, new = entry[0], entry[1]
        want = entry[2] if len(entry) > 2 else 1
        n = text.count(old)
        if (want == "all" and n < 1) or (want != "all" and n != want):
            raise SystemExit("%s: patch target occurs %d times, expected %s:\n%s"
                             % (name, n, want, old))
        text = text.replace(old, new)
    return text


def read_members(path):
    """Members of a 1e/Bell Labs ar archive: `!<arch>` and 60-byte headers."""
    data = open(path, "rb").read()
    if data[:8] != b"!<arch>\n":
        raise SystemExit("%s: not an ar archive" % path)
    off, out = 8, {}
    while off + 60 <= len(data):
        hdr = data[off:off + 60]
        name = hdr[0:16].decode("latin-1").rstrip()
        size = int(hdr[48:58].decode().strip())
        out[name] = data[off + 60:off + 60 + size]
        off += 60 + size
        if off % 2:
            off += 1
    return out


def program_object():
    """The smallest program: `TEXT main, $0` and a RETURN.

    A library cannot define `main`; this is the program's own symbol.  The
    records are the grammar `zl/obj.c`'s `ldobj` reads: ANAME, then
    `opcode, line, from, to` per instruction (D_EXTERN=4, D_CONST=8,
    D_NONE=1; ATEXT=85, ARETURN=75, AEND=94, AHISTORY=48, D_FILE=13).
    """
    def adr(t, w, s, off=None):
        b = bytes([t, w, s])
        return b if off is None else b + off.to_bytes(4, "little", signed=True)

    def rec(op, line, f, t):
        return bytes([op]) + line.to_bytes(4, "little") + f + t

    none = adr(1, 9, 0)                      # D_NONE, W_NONE, no symbol
    out = b""
    out += bytes([67, 13, 1]) + b"<main9-link.s\0"   # ANAME D_FILE
    out += rec(48, 1, none, none)                     # AHISTORY
    out += bytes([67, 4, 1]) + b"main\0"              # ANAME D_EXTERN 1
    out += rec(85, 2, adr(4, 1, 1, 0), adr(8, 9, 0, 0))   # ATEXT main $0
    out += rec(75, 3, none, none)                     # ARETURN
    out += rec(94, 4, none, none)                     # AEND
    return out


def link_main9(zl, libc, work, verbose=True):
    """Link main9.z with the real _clock/exits members and dump _main."""
    sys.path.insert(0, HERE)
    import p9exec

    members = read_members(libc)
    for need in ("main9.z", "__.SYMDEF"):
        if need not in members:
            raise SystemExit("%s: no %s member" % (libc, need))
    paths = []
    for name in ("main9.z", "argv0.z", "atexit.z", "_exits.z"):
        if name not in members:
            raise SystemExit("%s: no %s member" % (libc, name))
        p = os.path.join(work, name)
        open(p, "wb").write(members[name])
        paths.append(p)
    prog = os.path.join(work, "main-empty.z")
    open(prog, "wb").write(program_object())

    out = os.path.join(work, "main9-link.out")
    cmd = [zl, "-o", out] + [prog] + paths
    env = dict(os.environ, ZLLIB=os.path.dirname(os.path.abspath(libc)))
    if verbose:
        print("link: %s" % " ".join(cmd))
        print("  ZLLIB=%s" % env["ZLLIB"])
    r = subprocess.run(cmd, env=env)
    if r.returncode != 0 or not os.path.exists(out):
        raise SystemExit("zl failed (exit %d)" % r.returncode)

    exe = p9exec.read(out)
    syms = p9exec.symbols(exe)
    print("  header: magic 0x%x  text 0x%x  data 0x%x  bss 0x%x  "
          "syms 0x%x  entry 0x%x"
          % (exe["magic"], exe["text"], exe["data"], exe["bss"],
             exe["syms"], exe["entry"]))
    for name in ("main", "_main", "_clock", "exits"):
        if name in syms:
            print("  %-6s 0x%08x" % (name, syms[name][0]))
    if syms.get("_main", (None,))[0] != exe["entry"]:
        raise SystemExit("entry is not _main")
    print("  `_main` at 0x%04x, parcels (address order):"
          % syms["_main"][0])
    parcels = p9exec.parcel_stream(exe)
    for item in p9exec.decode(parcels, p9exec.TEXTBASE, exe["entry"], 8):
        print("    %08x  %04x  %s" % (item[0], item[1],
                                      " ".join(map(str, item[2:]))))
    # The A0 statement, checked: ENTER then MOV to _clock.
    problems = p9exec.check_main(exe, syms, parcels)
    if problems:
        raise SystemExit("CHECK FAILED: " + "; ".join(problems))
    print("  check: `_main` is ENTER R-16 then MOV R0,_clock(0x%04x)"
          % syms["_clock"][0])
    return exe


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.expanduser("~/src/inferno64"))
    ap.add_argument("--out", default="/tmp/zl-inferno")
    ap.add_argument("--link-main9", action="store_true",
                    help="also link libc.a's main9.z and print _main")
    ap.add_argument("--libc", default=DEFAULT_LIBC,
                    help="1e hobbit libc.a for --link-main9 (default %s)"
                         % DEFAULT_LIBC)
    args = ap.parse_args(argv)

    inc = os.path.join(args.root, "MacOSX", "arm64", "include")
    libdir = os.path.join(args.root, "MacOSX", "arm64", "lib")
    if not os.path.isdir(inc) or not os.path.isdir(libdir):
        print("Inferno64 not found under %s (build it with makemk.sh)"
              % args.root, file=sys.stderr)
        return 1

    build = args.out
    shutil.rmtree(build, ignore_errors=True)
    os.makedirs(build)
    zl = os.path.join(build, "zl")
    shutil.copytree(os.path.join(SRC, "zl"), zl)
    os.makedirs(os.path.join(build, "zc"))
    shutil.copy(os.path.join(SRC, "zc", "z.out.h"),
                os.path.join(build, "zc", "z.out.h"))
    shutil.copy(os.path.join(SRC, "zc", "enam.c"), os.path.join(zl, "enam.c"))
    os.makedirs(os.path.join(build, "shim"))
    open(os.path.join(build, "shim", "u.h"), "w").write(SHIM_U)
    open(os.path.join(build, "shim", "libc.h"), "w").write(SHIM_LIBC)
    open(os.path.join(zl, "shim.c"), "w").write(SHIM_C)

    for name in ("l.h", "obj.c", "list.c"):
        path = os.path.join(zl, name)
        text = open(path).read()
        pairs = [e[1:] for e in PATCHES if e[0] == name]
        open(path, "w").write(apply_patches(text, pairs, name))
    renamed = 0
    for name in sorted(os.listdir(zl)):
        if not name.endswith(".c") or name == "shim.c":
            continue
        path = os.path.join(zl, name)
        text = open(path).read()
        before = text
        for old, new in RENAMES + FMT_FIXES:
            text = text.replace(old, new)
        if text != before:
            renamed += 1
        open(path, "w").write(text)
    if renamed == 0:
        raise SystemExit("no source needed the host renames; check RENAMES")

    # Rlent: the 1e record is 28 bytes; a host `long` made it 32.  Patch
    # the copy in build/zc (the header the sources include).
    zouth = os.path.join(build, "zc", "z.out.h")
    text = open(zouth).read()
    open(zouth, "w").write(apply_patches(
        text,
        [("\t\tlong\toffset;\t\t/* for calculation */",
          "\t\tint\toffset;\t\t/* host port: 32 bits in the file */")],
        "z.out.h"))

    cflags = ["-arch", "arm64", "-w",
              "-I" + os.path.join(build, "shim"), "-I" + inc,
              "-I" + os.path.join(args.root, "include"), "-I."]
    objs = []
    for name in sorted(os.listdir(zl)):
        if name.endswith(".c"):
            subprocess.run(["cc", "-c"] + cflags + [name], cwd=zl, check=True)
            objs.append(name[:-2] + ".o")
    libs = [os.path.join(libdir, l) for l in
            ("libregexp.a", "libbio.a", "lib9.a", "liballoc.a")]
    subprocess.run(["cc", "-arch", "arm64", "-o", "zl"] + objs + libs,
                   cwd=zl, check=True)
    print(zl)

    if args.link_main9:
        link_main9(os.path.join(zl, "zl"), os.path.abspath(args.libc), build)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
