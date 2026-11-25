#!/bin/sh
# The directory commands of Micro PIMOS on one PDSS tree: ls with a
# wildcard, cd and pwd, "~" (HOME), "~user" for root and for an unknown
# user, and a wildcard rm.  No conformance job reaches them (README
# "Portable C"); test.sh runs this on build-native and build-asan.
#
#   ./dirsmoke.sh TREE        TREE: a modern.sh build-<target>/
#
# HOME is a scratch directory inside the tree (TREE/dirsmoke/home), so
# no host path is compared: the transcript is cut at the prompts, one
# block per command, the tree's and HOME's physical paths are printed as
# <tree> and <home>, the lines of each ls are sorted (readdir order is
# the file system's), and the cd("~root") and following pwd blocks are
# replaced by "<host>" (root's home and whether it can be entered are
# the host's).  The result, plus the emulator's exit status and the
# files left in HOME, must equal dirsmoke.expected byte for byte.
#
# Discriminating (observed 2026-11-25; sysdep.c edited from a backup
# and restored from it, diff clean):
#   - both NULL guards removed (pdss_chdir returns chdir(dir),
#     pdss_opendir calls opendir(path)): build-native still PASSes --
#     macOS's opendir returns an error for a NULL path (chdir is never
#     given one, see below) -- and
#     build-asan FAILs: ASan's opendir interceptor reads the NULL path,
#     "AddressSanitizer: SEGV on unknown address 0x000000000000" in
#     pdss_opendir from blt_b_test_directory (blt_iodev.c:780), on
#     cd("~nosuchuserxyz"): the transcript stops there, exit status 134
#     (abort) instead of 0, x1.tmp and x2.tmp not removed.
#   - only the pdss_opendir guard removed: the same build-asan FAIL;
#     through ./test.sh, everything before it passes (queens, small
#     heap, conformance against golden32/, test/ headers, dirsmoke on
#     build-native) and test.sh stops with
#     "pdss: FAIL (dirsmoke, asan build)", rc 1.
#   - only the pdss_chdir guard removed: PASS on both.  The shell never
#     passes chdir a NULL path: Micro PIMOS's cd (runtime/fildev.kl1)
#     calls directory_pathname only after test_directory succeeded, and
#     test_directory fails first.  The chdir guard is defensive.
HERE=$(cd "$(dirname "$0")" && pwd)
B=$1
[ -x "$B/emulator/pdss" ] || { echo "dirsmoke: no $B/emulator/pdss"; exit 2; }
B=$(cd "$B" && pwd -P)
RUN=$(cat "$B/RUN" 2>/dev/null)
T=timeout; command -v timeout >/dev/null 2>&1 || T=
S="$B/dirsmoke"
rm -rf "$S"; mkdir -p "$S/home"
: > "$S/home/x1.tmp"; : > "$S/home/x2.tmp"; : > "$S/home/y.keep"
HOME=$(cd "$S/home" && pwd -P); export HOME
unset PDSS_WORLD
cd "$B/emulator" || exit 2
CMDS='ls("../test/b_a*").
cd("../sample").
pwd.
cd("~root").
pwd.
cd("~").
pwd.
ls("~/x*").
cd("~nosuchuserxyz").
pwd.
ls("~nosuchuserxyz/*").
rm("~/x*.tmp").
ls("~/x*").
halt.'
printf '%s\n' "$CMDS" | ${T:+$T 120} $RUN ./pdss > "$S/raw.log" 2>&1
rc=$?
python3 -I - "$S/raw.log" "$B" "$HOME" "$CMDS" > "$S/got" <<'PY'
import sys
raw, tree, home, cmds = sys.argv[1:5]
cmds = cmds.split("\n")
text = open(raw, encoding="latin-1").read()
text = text.replace(home, "<home>").replace(tree, "<tree>")
blocks = text.split("| ?- ")[1:]          # [0] is the banner
for i, b in enumerate(blocks):
    c = cmds[i] if i < len(cmds) else "(none)"
    prev = cmds[i-1] if 0 < i <= len(cmds) else ""
    lines = [l.rstrip() for l in b.split("\n") if l.strip()]
    if c == 'cd("~root").' or (prev == 'cd("~root").'):
        lines = ["<host>"]                # root's home is the host's
    elif c.startswith("ls("):
        lines = sorted(lines[:-1]) + lines[-1:]   # readdir order
    print(("%-24s %s" % (c, " | ".join(lines))).rstrip())
PY
echo "exit: $rc" >> "$S/got"
echo "left: $(cd "$S/home" && ls | sort | tr '\n' ' ' | sed 's/ $//')" >> "$S/got"
if cmp -s "$S/got" "$HERE/dirsmoke.expected"; then
  echo "dirsmoke: PASS ($(basename "$B"))"
else
  echo "dirsmoke: FAIL ($(basename "$B"))"
  diff "$HERE/dirsmoke.expected" "$S/got" | cut -c1-300 | head -20
  exit 1
fi
