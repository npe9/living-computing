#!/bin/sh
# Build the modernised PDSS (src/emulator/) for one target into its own tree,
# build-<target>/, and reassemble the KL1 libraries with it.
#
#   ./modern.sh [target]       target: native (default), gcc, x86_64,
#                              asan, low (see README.md "Targets")
#
# A tree is the tarball unpacked (KL1 libraries, test/, sample/) with
# emulator/pdss and emulator/pdssasm built from src/emulator/.  Prints the tree's
# path on success.  Exit 77 = this host cannot build or run the target.
# PDSS_RUN in the environment is the prefix that runs the target's
# binaries (set by this script for x86_64; read it back from
# build-<target>/RUN).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
TAR="$HERE/../../docs/nonlocal/pdss.tar.Z"
T=${1:-native}
B="$HERE/build-$T"
RUN=
WARN="-Wall -Wextra"
case "$T" in
  native) CC=${CC:-cc}; CF="-O2 $WARN" ;;
  gcc)    CC=${GCC:-}; for c in gcc-15 gcc-14 gcc-13 gcc; do
            [ -n "$CC" ] && break
            command -v $c >/dev/null 2>&1 && $c --version 2>/dev/null | grep -qv clang && CC=$c
          done
          [ -n "$CC" ] || { echo "modern($T): SKIP (no GNU gcc)"; exit 77; }
          CF="-O2 $WARN" ;;
  x86_64) [ "$(uname -s)" = Darwin ] || { echo "modern($T): SKIP (Darwin only; on Linux use native)"; exit 77; }
          arch -x86_64 /usr/bin/true 2>/dev/null || { echo "modern($T): SKIP (no x86_64 execution)"; exit 77; }
          [ "$(uname -m)" = x86_64 ] || RUN="arch -x86_64"
          CC=${CC:-cc}; CF="-O2 -arch x86_64 $WARN" ;;
  asan)   CC=${CC:-cc}; CF="-O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined -fno-sanitize-recover=undefined $WARN" ;;
  low)    # Transitional: the reference recipe (build.sh) applied to src/.
          arch -x86_64 /usr/bin/true 2>/dev/null || { echo "modern($T): SKIP (no x86_64 execution)"; exit 77; }
          CC=cc
          CF="-arch x86_64 -O1 -std=gnu89 -w -Wno-error=implicit-function-declaration -Wno-error=implicit-int -Wno-error=int-conversion -Wno-error=incompatible-pointer-types -Wno-error=return-type -fcommon -Dmalloc=pdss_malloc -Dfree=pdss_free -Drealloc=pdss_realloc -Dcalloc=pdss_calloc -Dmain=pdss_main"
          LDF="-Wl,-pagezero_size,0x10000 -Wl,-no_pie -Wl,-image_base,0x100000" ;;
  *) echo "modern: unknown target $T"; exit 2 ;;
esac
mkdir -p "$B"
if [ ! -d "$B/runtime" ]; then
  gzip -dc "$TAR" | (cd "$B" && tar xf -)
  rm -f "$B"/emulator/*.c "$B"/emulator/*.h "$B"/emulator/Makefile
fi
SHIM=
if [ "$T" = low ]; then
  cc -arch x86_64 -O1 -c "$HERE/src/emulator/port_low.c" -o "$B/emulator/port_low.o"; SHIM="$B/emulator/port_low.o"
fi
make -s -C "$HERE/src/emulator" CC="$CC" CFLAGS="$CF" LDFLAGS="${LDF:-}" SHIM="$SHIM" O="$B/emulator" >"$B/make.log" 2>&1 \
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
