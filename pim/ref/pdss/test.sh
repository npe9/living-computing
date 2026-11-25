#!/bin/sh
# PDSS V2.52.20, built from the in-tree source (src/, see README.md), end
# to end on this host:
#   0. tools/posixcheck.py: no source but sysdep.[ch] includes a POSIX
#      header or calls a POSIX function.
#   1. queens.kl1 through PDSS's own KL1 compiler (itself KL1, running on
#      the emulator), assembler and loader; N-queens solution counts and
#      the first 4-queens solutions; again with a 12,000-cell heap, which
#      forces copying collections.
#   2. conformance.sh (PDSS's test/ programs, the samples, the compiler on
#      the distribution's own sources, the reassembled libraries) on the
#      default build, against golden32/: byte for byte, GC reports and
#      the .asm/.sav sums included.
#   3. Each test/ program's console output against its own header comment
#      (check_headers.py; headers_expected.txt lists ICOT's own 7 misses).
#   4. dirsmoke.sh: the directory commands (ls, cd, pwd, "~", "~user",
#      a wildcard rm), which no conformance job reaches, on the default
#      build and on an ASan build (dirsmoke.expected); the NULL-path
#      guard in pdss_opendir is caught only under ASan on macOS.
#   5. The same conformance on the lp64rec build (the record sizes of the
#      2026 reference port, README "Record sizes") against golden/, which
#      was recorded from that port: the in-tree source is the reference
#      port's behaviour, GC schedule included.
# More targets (gcc, x86_64, plain char signed/unsigned, ASan/UBSan, a
# 32-bit compile, the 1992 SPARC save files) are in test_slow.sh.
#
# Discriminating (observed 2026-11-25, each injected into src/emulator/
# from a backup and reverted from it; see README "Fault injections"):
#   - truncated pointer (port.h pdss_ref returns an outside address cut
#     to 32 bits instead of a foreign-table entry): libraries reassemble,
#     then the KL1 compiler dies with a bus error; "FAIL (KL1 compile)".
#   - wrong tag shift (cell.h StringTypeof shifts the descriptor by 23,
#     not 24): "FAIL (KL1 compile)".
#   - dropped GC root (gc.c no longer calls gc_io_table): queens and its
#     small-heap run still pass; conformance FAILs 46 of 186 jobs, the
#     same set as the 46 golden32/ transcripts with a GC report, on the
#     GC report's live-cell counts; with the GC
#     reports removed (gcblind.py) all 186 still match -- only the
#     byte-exact transcript catches it.
#   - NULL path to opendir (sysdep.c pdss_opendir calls opendir(path)
#     unguarded): every earlier step passes, dirsmoke PASSes on
#     build-native (macOS's opendir fails cleanly) and FAILs on
#     build-asan, SEGV in pdss_opendir on cd("~nosuchuserxyz"), exit
#     134; "pdss: FAIL (dirsmoke, asan build)", rc 1.
HERE=$(cd "$(dirname "$0")" && pwd)
T=timeout; command -v timeout >/dev/null 2>&1 || T=
python3 -I "$HERE/tools/posixcheck.py" >/dev/null || { python3 -I "$HERE/tools/posixcheck.py"; echo "pdss: FAIL (POSIX use outside sysdep.[ch])"; exit 1; }
B=$("$HERE/modern.sh" native); rc=$?
[ $rc = 77 ] && { echo "pdss: SKIP ($B)"; exit 0; }
[ $rc = 0 ] || { echo "$B" | tail -20; echo "pdss: FAIL (build)"; exit 1; }
B=$(echo "$B" | tail -1)
mkdir -p "$B/work" && cp "$HERE/queens.kl1" "$B/work/"
cd "$B/emulator" || exit 1
printf "no.\n3.\n'../work/queens.kl1'.\n'../work/queens.asm'.\n" | ${T:+$T 300} ./pdss KL1CMP +t > ../work/compile.log 2>&1
grep -q 'success' ../work/compile.log || { echo "pdss: FAIL (KL1 compile)"; tail -5 ../work/compile.log; exit 1; }
(cd ../work && ../emulator/pdssasm queens </dev/null | grep -q ' OK') || { echo "pdss: FAIL (assemble)"; exit 1; }
printf "load('../work/queens').\nqueens:s(4).\nqueens:n(4).\nqueens:n(6).\nqueens:n(8).\nhalt.\n" | ${T:+$T 300} ./pdss > ../work/run.log 2>&1
got=$(sed -n '/Loading/,$p' ../work/run.log | grep -v '^$' | grep -v '^yes\.$' | sed 's/^| ?- //' | grep -v '^$' | tr '\n' ' ')
want='"../work/queens" : Loading ... done Module name : queens [3|[1,4,2]x] [2|[4,1,3]x] end 2 4 92 '
printf "load('../work/queens').\nqueens:n(8).\nqueens:n(8).\nhalt.\n" | ${T:+$T 300} ./pdss -h12000 > ../work/gc.log 2>&1
gcs=$(grep -c '^GC-' ../work/gc.log); ans=$(grep -c '92$' ../work/gc.log)
if [ "$gcs" -lt 2 ] || [ "$ans" != 2 ]; then
  echo "pdss: FAIL (small heap: $gcs collections, $ans of 2 answers)"; exit 1
fi
[ "$got" = "$want" ] || { echo "pdss: FAIL (queens)"; echo "  got : $got"; echo "  want: $want"; exit 1; }
PDSS_GOLDEN="$HERE/golden32" "$HERE/conformance.sh" "$B" fast || { echo "pdss: FAIL (conformance, default build)"; exit 1; }
python3 -I "$HERE/check_headers.py" "$B/test" "$B/conf" --expect "$HERE/headers_expected.txt" -q \
  || { echo "pdss: FAIL (test/ headers)"; exit 1; }
"$HERE/dirsmoke.sh" "$B" || { echo "pdss: FAIL (dirsmoke, default build)"; exit 1; }
A=$("$HERE/modern.sh" asan); rc=$?
if [ $rc = 0 ]; then
  A=$(echo "$A" | tail -1)
  "$HERE/dirsmoke.sh" "$A" || { echo "pdss: FAIL (dirsmoke, asan build)"; exit 1; }
  DS="directory commands on the default and ASan builds"
else   # a host without the sanitizer runtime: say so, do not fail
  DS="directory commands on the default build only (no ASan build: $(echo "$A" | tail -1))"
fi
L=$("$HERE/modern.sh" lp64rec) || { echo "$L" | tail -20; echo "pdss: FAIL (build, lp64rec)"; exit 1; }
L=$(echo "$L" | tail -1)
"$HERE/conformance.sh" "$L" fast || { echo "pdss: FAIL (conformance, lp64rec build against the reference port's golden/)"; exit 1; }
echo "pdss: PASS (in-tree source; KL1 compiler ran on it; 4, 6, 8 queens give 2, 4, 92 solutions; $gcs collections survived; $DS; conformance against golden32/ and, with the reference port's record sizes, golden/)"
