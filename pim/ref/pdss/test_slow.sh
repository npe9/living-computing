#!/bin/sh
# The PDSS target matrix (README.md "Targets"): every target this host
# can build and run, each through conformance.sh against its golden --
# golden32/ for the default record sizes, golden/ for <target>-lp64rec --
# plus three portability checks that need no new golden:
#   - the 1992 save files: the libraries' .sav as ICOT shipped them
#     (written big-endian on a SPARC, docs/nonlocal/pdss.tar.Z) loaded in
#     place of the reassembled ones; transcripts must match golden/ with
#     the GC reports removed (gcblind.py), except the jobs listed in
#     SPARCSAV_EXPECT below;
#   - save files across targets: the default trees' .sav and .asm sums
#     are part of every .got, so equal .got files across targets mean
#     byte-identical save files;
#   - a 32-bit compile: every ISO C source with a 32-bit cross compiler
#     if one is installed (arm-none-eabi-gcc: int32_t is long there).
# Not part of run_tests.sh (several minutes); run it after any change to
# src/emulator/.  Targets the host cannot run print SKIP.
#
#   ./test_slow.sh [target ...]
HERE=$(cd "$(dirname "$0")" && pwd)
TARGETS=${*:-"native lp64rec gcc gcc-lp64rec x86_64 x86_64-lp64rec uchar schar asan asan-lp64rec"}
# Jobs whose output depends on the GC schedule, which the shipped .sav
# files (atoms in another order) move: c_compiler_outp ends in heap
# exhaustion on the reference port; libsav compares the .sav bytes.
SPARCSAV_EXPECT="c_compiler_outp libsav"
bad=0
for t in $TARGETS; do
  out=$("$HERE/modern.sh" $t 2>&1); rc=$?
  if [ $rc = 77 ]; then echo "slow($t): SKIP ($(echo "$out" | tail -1))"; continue; fi
  if [ $rc != 0 ]; then echo "$out" | tail -10; echo "slow($t): FAIL (build)"; bad=1; continue; fi
  B=$(echo "$out" | tail -1)
  case $t in *lp64rec) G="$HERE/golden" ;; *) G="$HERE/golden32" ;; esac
  r=$(PDSS_RUN=$(cat "$B/RUN") PDSS_GOLDEN="$G" "$HERE/conformance.sh" "$B" fast 2>&1); rc=$?
  echo "slow($t): $(echo "$r" | tail -1)"
  [ $rc = 0 ] || { echo "$r" | tail -8; bad=1; }
done
# The 1992 SPARC save files.
TAR="$HERE/../../docs/nonlocal/pdss.tar.Z"
L="$HERE/build-lp64rec"
if [ -f "$TAR" ] && [ -x "$L/emulator/pdss" ]; then
  S="$HERE/build-sparcsav"
  rm -rf "$S"; cp -R "$L" "$S"
  X="$S/shipped"; mkdir -p "$X"
  gzip -dc "$TAR" | (cd "$X" && tar xf - runtime mpimos compiler)
  for f in "$X"/runtime/*.sav "$X"/mpimos/*.sav "$X"/compiler/*.sav; do
    cp "$f" "$S/${f#$X/}"
  done
  "$HERE/conformance.sh" "$S" fast >/dev/null 2>&1
  got=$(python3 -I "$HERE/gcblind.py" "$HERE/golden" "$S/conf" | grep -v '^ ' | grep -v '^gcblind' | cut -d: -f1 | tr '\n' ' ')
  if [ "$got" = "$SPARCSAV_EXPECT " ]; then
    echo "slow(sparcsav): PASS (the 1992 big-endian .sav files load; transcripts match golden/ without GC reports, except $SPARCSAV_EXPECT)"
  else
    echo "slow(sparcsav): FAIL (differ: ${got:-none}; expected: $SPARCSAV_EXPECT)"; bad=1
  fi
else
  echo "slow(sparcsav): SKIP (needs $TAR and build-lp64rec)"
fi
# A 32-bit compile (no run: a bare-metal C library has no POSIX).
XCC=${XCC:-arm-none-eabi-gcc}
if command -v "$XCC" >/dev/null 2>&1; then
  O="$HERE/build-xcompile"; rm -rf "$O"; mkdir -p "$O"
  n=0; fails=
  for f in "$HERE"/src/emulator/*.c; do
    b=$(basename "$f" .c)
    case $b in pdssinv|table|pdssmerge) continue ;; esac   # not built (Makefile)
    if (cd "$HERE/src/emulator" && "$XCC" -std=c11 -O1 -Wall -Wextra -Wno-pointer-sign -Werror=format -Wno-format-truncation \
          -Werror=incompatible-pointer-types -DMAKEDATE='"x"' -c "$b.c" -o "$O/$b.o") > "$O/$b.err" 2>&1; then
      n=$((n+1))
    else
      fails="$fails $b"
    fi
  done
  # Only sysdep.c, the POSIX layer, needs what the bare-metal library lacks.
  if [ "$fails" = " sysdep" ]; then
    echo "slow(32-bit): PASS ($XCC: $n sources compile with -Werror=format; not sysdep.c, the POSIX layer)"
  else
    echo "slow(32-bit): FAIL ($XCC: failed:$fails; expected: sysdep)"; bad=1
  fi
else
  echo "slow(32-bit): SKIP (no $XCC)"
fi
[ $bad = 0 ] && echo "pdss slow: PASS" || { echo "pdss slow: FAIL"; exit 1; }
