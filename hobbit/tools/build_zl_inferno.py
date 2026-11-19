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
  * `strconv`, `doprint` and `argv0` are supplied (Inferno's lib9 has no
    1st Edition `strconv`/`doprint`);
  * `fmtinstall` hooks are cast to Inferno's `Fmt*` signature.

Nothing in the repository's vendored sources is edited: the script
copies them into a build directory and patches the copies.

    python3 tools/build_zl_inferno.py [--root ~/src/inferno64] [--out DIR]

Prints the path of the linked `zl` on success.
"""

import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "plan9-1e", "sys", "src", "cmd")

PATCHES = {
    "l.h": [
        ('#include "../zc/z.out.h"\n',
         '#include "../zc/z.out.h"\n'
         '/* Inferno bio.h has no Fconv (1st Edition Bio did). */\n'
         'typedef void (*Fconv)();\n'
         'long strconv(char*, char**);\n'
         'char* doprint(char*, char*, char*, va_list);\n'),
        ("double\tcputime(void);", "long\tcputime(void);"),
    ],
    "obj.c": [
        ("arhdr.name", "arhdr.ar_name"),
        ("arhdr.size", "arhdr.ar_size"),
        ("\t\tif(strncmp(arhdr.fmag, ARFMAG, sizeof(arhdr.fmag)))",
         "#ifndef __APPLE__\n"
         "\t\tif(strncmp(arhdr.fmag, ARFMAG, sizeof(arhdr.fmag)))\n"
         "#endif"),
    ],
    "list.c": [
        ("fmtinstall('A', Aconv);", "fmtinstall('A', (int(*)(Fmt*))Aconv);"),
        ("fmtinstall('D', Dconv);", "fmtinstall('D', (int(*)(Fmt*))Dconv);"),
        ("fmtinstall('P', Pconv);", "fmtinstall('P', (int(*)(Fmt*))Pconv);"),
        ("fmtinstall('S', Sconv);", "fmtinstall('S', (int(*)(Fmt*))Sconv);"),
        ("fmtinstall('W', Wconv);", "fmtinstall('W', (int(*)(Fmt*))Wconv);"),
    ],
}

RENAMES = [("malloc(", "zlmalloc("), ("calloc(", "zlcalloc("),
           ("realloc(", "zlrealloc("), ("free(", "zlfree(")]

SHIM_U = "#include <lib9.h>\n"
SHIM_LIBC = "/* lib9.h is pulled in by the u.h shim */\n"
SHIM_C = """\
/* Calls the 1st Edition linker makes that Inferno's lib9 does not have. */
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <time.h>

long strconv(char *s, char **p) { return strtol(s, p, 0); }
long cputime(void) { return (long)(clock() * 1000 / CLOCKS_PER_SEC); }

char *doprint(char *buf, char *end, char *fmt, va_list a)
{
\tint n = vsnprintf(buf, end - buf, fmt, a);
\tchar *s = buf + (n < 0 ? 0 : n);
\treturn s < end ? s : end - 1;
}

char *argv0;
"""


def patch(text, pairs):
    for old, new in pairs:
        text = text.replace(old, new)
    return text


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.expanduser("~/src/inferno64"))
    ap.add_argument("--out", default="/tmp/zl-inferno")
    args = ap.parse_args(argv)

    inc = os.path.join(args.root, "MacOSX", "arm64", "include")
    libdir = os.path.join(args.root, "MacOSX", "arm64", "lib")
    if not os.path.isdir(inc) or not os.path.isdir(libdir):
        print("Inferno64 not found under %s (build it with makemk.sh)"
              % args.root, file=sys.stderr)
        return 1

    build = args.out
    shutil.rmtree(build, ignore_errors=True)
    shutil.copytree(os.path.join(SRC, "zl"), os.path.join(build, "zl"))
    os.makedirs(os.path.join(build, "zc"))
    shutil.copy(os.path.join(SRC, "zc", "z.out.h"),
                os.path.join(build, "zc", "z.out.h"))
    shutil.copy(os.path.join(SRC, "zc", "enam.c"), os.path.join(build, "zl"))
    os.makedirs(os.path.join(build, "shim"))
    open(os.path.join(build, "shim", "u.h"), "w").write(SHIM_U)
    open(os.path.join(build, "shim", "libc.h"), "w").write(SHIM_LIBC)
    open(os.path.join(build, "zl", "shim.c"), "w").write(SHIM_C)

    zl = os.path.join(build, "zl")
    for name, pairs in PATCHES.items():
        path = os.path.join(zl, name)
        text = open(path).read()
        with open(path, "w") as f:
            f.write(patch(text, pairs))
    for name in os.listdir(zl):
        if name.endswith(".c"):
            path = os.path.join(zl, name)
            text = open(path).read()
            with open(path, "w") as f:
                f.write(patch(text, RENAMES))

    cflags = ["-arch", "arm64", "-w",
              "-I" + os.path.join(build, "shim"), "-I" + inc,
              "-I" + os.path.join(args.root, "include"), "-I."]
    objs = []
    for name in sorted(os.listdir(zl)):
        if name.endswith(".c"):
            obj = os.path.join(zl, name[:-2] + ".o")
            subprocess.run(["cc", "-c"] + cflags + [name], cwd=zl, check=True)
            objs.append(obj)
    libs = [os.path.join(libdir, l) for l in
            ("libregexp.a", "libbio.a", "lib9.a", "liballoc.a")]
    out = os.path.join(zl, "zl")
    subprocess.run(["cc", "-arch", "arm64", "-o", "zl"] + objs + libs,
                   cwd=zl, check=True)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
