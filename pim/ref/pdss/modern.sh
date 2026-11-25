          # Homebrew gcc on macOS: its fixed headers need the SDK it was built
          # against or newer; point it at the current one (environment only).
          if [ "$(uname -s)" = Darwin ] && [ -z "${SDKROOT:-}" ] && command -v xcrun >/dev/null 2>&1; then
            SDKROOT=$(xcrun --show-sdk-path); export SDKROOT
          fi
#!/bin/sh
# Build the modernised PDSS (src/emulator/) for one target into its own tree,
# build-<target>/, and reassemble the KL1 libraries with it.
#
#   ./modern.sh [target]       target: native (default), gcc, x86_64,
#                              asan, lp64rec, uchar, schar
#                              (see README.md "Targets")
#
# A tree is a copy of src/ (KL1 libraries, test/, sample/) with
# emulator/pdss and emulator/pdssasm built from src/emulator/.  Prints the tree's
# path on success.  Exit 77 = this host cannot build or run the target.
# PDSS_RUN in the environment is the prefix that runs the target's
# binaries (set by this script for x86_64; read it back from
# build-<target>/RUN).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
T=${1:-native}
B="$HERE/build-$T"
RUN=
WARN="-Wall -Wextra"
# <target>-lp64rec is <target> with the reference port's record sizes.
LR=; T0=$T
case "$T" in *?-lp64rec) LR=-DPDSS_LP64_RECORDS; T0=${T%-lp64rec} ;; esac
case "$T0" in
  native) CC=${CC:-cc}; CF="-O2 $WARN" ;;
  gcc)    CC=${GCC:-}; for c in gcc-15 gcc-14 gcc-13 gcc; do
            [ -n "$CC" ] && break
            command -v $c >/dev/null 2>&1 && $c --version 2>/dev/null | grep -qv clang && CC=$c
          done
          [ -n "$CC" ] || { echo "modern($T): SKIP (no GNU gcc)"; exit 77; }
          # Homebrew gcc on macOS: its fixed headers need the SDK it was
          # built against or a newer one; name the current SDK (environment
          # only, no flag).
          if [ "$(uname -s)" = Darwin ] && [ -z "${SDKROOT:-}" ] && command -v xcrun >/dev/null 2>&1; then
            SDKROOT=$(xcrun --show-sdk-path); export SDKROOT
          fi
          CF="-O2 $WARN" ;;
  x86_64) [ "$(uname -s)" = Darwin ] || { echo "modern($T): SKIP (Darwin only; on Linux use native)"; exit 77; }
          arch -x86_64 /usr/bin/true 2>/dev/null || { echo "modern($T): SKIP (no x86_64 execution)"; exit 77; }
          [ "$(uname -m)" = x86_64 ] || RUN="arch -x86_64"
          CC=${CC:-cc}; CF="-O2 -arch x86_64 $WARN" ;;
  asan)   CC=${CC:-cc}; CF="-O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -fno-sanitize-recover=undefined $WARN" ;;
  lp64rec) CC=${CC:-cc}; CF="-O2 -DPDSS_LP64_RECORDS $WARN" ;;  # layout check, see README
  uchar)  CC=${CC:-cc}; CF="-O2 -funsigned-char $WARN" ;;  # plain char unsigned (as on ARM Linux)
  schar)  CC=${CC:-cc}; CF="-O2 -fsigned-char $WARN" ;;
  *) echo "modern: unknown target $T"; exit 2 ;;
esac
CF="$CF $LR"
mkdir -p "$B"
# The tree is a copy of the in-tree distribution, src/, refreshed on every
# run; the emulator is built from src/emulator/ itself (objects in the tree).
cp -R "$HERE/src/." "$B/"
make -s -C "$HERE/src/emulator" CC="$CC" CFLAGS="$CF" LDFLAGS="${LDF:-}" O="$B/emulator" >"$B/make.log" 2>&1 \
  || { cat "$B/make.log"; echo "modern($T): FAIL (build)"; exit 1; }
echo "$RUN" > "$B/RUN"
# Reassemble every library from its .asm (the tarball's "make reassm").
for d in runtime mpimos compiler; do
  (cd "$B/$d" && for f in *.asm; do
     $RUN ../emulator/pdssasm ${f%.asm} </dev/null | grep -q ' OK' \
       || { echo "modern($T): FAIL (pdssasm on $d/$f)"; exit 1; }
   done)
done
echo "$B"
