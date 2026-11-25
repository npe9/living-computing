#!/usr/bin/env python3
"""Check that PDSS's POSIX use is isolated in src/emulator/sysdep.[ch].

    posixcheck.py [EMULATOR_DIR]

Every other source the Makefile builds (and the headers and table.c,
which is included by three of them) may include only ISO C headers and
may not call the POSIX functions PDSS uses.  Regions under `#if 0` (the
1992 a.out loader in native.c) are skipped; so is the ASan interface
header, included only under AddressSanitizer.  getwd is not listed: sysdep.h
defines it as a macro over its own pdss_getwd.  Prints each violation;
exit 1 if any.
"""
import os
import re
import sys

ISO = set("""assert.h complex.h ctype.h errno.h fenv.h float.h inttypes.h
iso646.h limits.h locale.h math.h setjmp.h signal.h stdalign.h stdarg.h
stdatomic.h stdbool.h stddef.h stdint.h stdio.h stdlib.h stdnoreturn.h
string.h tgmath.h threads.h time.h uchar.h wchar.h wctype.h""".split())
ALLOWED = {"sanitizer/asan_interface.h"}
POSIX_CALLS = """opendir readdir closedir chdir unlink getpid getppid getuid
pause alarm setitimer getitimer getrusage getpwnam getpwuid getcwd
sigprocmask sigblock sigsetmask sigaction kill ioctl fcntl select stat
lstat fstat access isatty fileno popen pclose fork execv execvp wait
waitpid pipe dup dup2 read write open close lseek usleep nanosleep
gettimeofday bzero bcopy bcmp index rindex strcasecmp regcomp regexec
""".split()
CALL = re.compile(r"(?<![\w.>])(" + "|".join(POSIX_CALLS) + r")\s*\(")


def strip(text):
    """Comments, string literals and #if 0 regions removed."""
    text = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)
    text = re.sub(r'"(\\.|[^"\\\n])*"', '""', text)
    out, skip, depth = [], 0, 0
    for line in text.split("\n"):
        s = line.strip()
        if skip:
            if re.match(r"#\s*if", s):
                depth += 1
            elif re.match(r"#\s*endif", s):
                if depth == 0:
                    skip = 0
                else:
                    depth -= 1
            elif re.match(r"#\s*(else|elif)", s) and depth == 0:
                skip = 0
            out.append("")
            continue
        if re.match(r"#\s*if\s+0\b", s):
            skip, depth = 1, 0
            out.append("")
            continue
        out.append(line)
    return "\n".join(out)


def built_sources(d):
    mk = open(os.path.join(d, "Makefile"), encoding="latin-1").read().replace("\\\n", " ")
    names = set()
    for var in ("KL1", "ASM"):
        m = re.search(r"^%s\s*=(.*)$" % var, mk, re.M)
        names.update(m.group(1).split())
    files = {n + ".c" for n in names} | {"table.c", "version.c"}
    files |= {f for f in os.listdir(d) if f.endswith(".h")}
    return sorted(f for f in files if not f.startswith("sysdep."))


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "src", "emulator")
    bad = []
    files = built_sources(d)
    for f in files:
        raw = open(os.path.join(d, f), encoding="latin-1").read()
        text = strip(raw)
        for n, line in enumerate(text.split("\n"), 1):
            m = re.match(r"\s*#\s*include\s*<([^>]+)>", line)
            if m and m.group(1) not in ISO and m.group(1) not in ALLOWED:
                bad.append("%s:%d: includes <%s>" % (f, n, m.group(1)))
            for c in CALL.finditer(line):
                bad.append("%s:%d: calls %s()" % (f, n, c.group(1)))
    for b in bad:
        print(b)
    print("posixcheck: %d files, %d POSIX uses outside sysdep.[ch]" % (len(files), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
