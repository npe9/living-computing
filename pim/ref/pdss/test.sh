#!/bin/sh
# Build the PDSS port and run one KL1 program end to end on it:
# compile queens.kl1 with PDSS's own KL1 compiler (itself KL1, running
# on the port), assemble, load, and check the N-queens solution counts
# and the first 4-queens solutions it prints.
HERE=$(cd "$(dirname "$0")" && pwd)
"$HERE/build.sh"; rc=$?
[ $rc = 77 ] && exit 0
[ $rc = 0 ] || { echo "pdss: FAIL (build)"; exit 1; }
B="$HERE/build"
mkdir -p "$B/work" && cp "$HERE/queens.kl1" "$B/work/"
cd "$B/emulator"
T=timeout; command -v timeout >/dev/null 2>&1 || T=
printf "no.\n3.\n'../work/queens.kl1'.\n'../work/queens.asm'.\n" | ${T:+$T 300} ./pdss KL1CMP +t > ../work/compile.log 2>&1
grep -q 'success' ../work/compile.log || { echo "pdss: FAIL (KL1 compile)"; tail -5 ../work/compile.log; exit 1; }
(cd ../work && ../emulator/pdssasm queens </dev/null | grep -q ' OK') || { echo "pdss: FAIL (assemble)"; exit 1; }
printf "load('../work/queens').\nqueens:s(4).\nqueens:n(4).\nqueens:n(6).\nqueens:n(8).\nhalt.\n" | ${T:+$T 300} ./pdss > ../work/run.log 2>&1
got=$(sed -n '/Loading/,$p' ../work/run.log | grep -v '^$' | grep -v '^yes\.$' | sed 's/^| ?- //' | grep -v '^$' | tr '\n' ' ')
want='"../work/queens" : Loading ... done Module name : queens [3|[1,4,2]x] [2|[4,1,3]x] end 2 4 92 '
# Again with a 12,000-cell heap, which forces copying collections.
printf "load('../work/queens').\nqueens:n(8).\nqueens:n(8).\nhalt.\n" | ${T:+$T 300} ./pdss -h12000 > ../work/gc.log 2>&1
gcs=$(grep -c '^GC-' ../work/gc.log); ans=$(grep -c '92$' ../work/gc.log)
if [ "$gcs" -lt 2 ] || [ "$ans" != 2 ]; then
  echo "pdss: FAIL (small heap: $gcs collections, $ans of 2 answers)"; exit 1
fi
if [ "$got" = "$want" ]; then
  echo "pdss: PASS (KL1 compiler ran on the port; 4, 6, 8 queens give 2, 4, 92 solutions; $gcs collections survived)"
else
  echo "pdss: FAIL"; echo "  got : $got"; echo "  want: $want"; exit 1
fi
# PDSS's own test/ programs, the samples and the compiler on the
# distribution's sources, against golden/ (recorded from this build).
"$HERE/conformance.sh" "$B" fast || { echo "pdss: FAIL (conformance, reference build)"; exit 1; }
python3 -I "$HERE/check_headers.py" "$B/test" "$HERE/golden" --expect "$HERE/headers_expected.txt" -q \
  || { echo "pdss: FAIL (test/ headers)"; exit 1; }
